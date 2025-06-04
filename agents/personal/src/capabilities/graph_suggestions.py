"""
Graph suggestion capabilities for the Personal Knowledge Agent.
"""
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from ..db import KnowledgeDB
import logging
import requests
import json
import re
from difflib import SequenceMatcher
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from rake_nltk import Rake
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("spaCy model not found. Installing...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

class SuggestedConnection(BaseModel):
    """Model representing a suggested connection between entities."""
    source_id: str = Field(..., description="ID of the source entity")
    target_id: str = Field(..., description="ID of the target entity")
    relationship_type: str = Field(..., description="Suggested type of relationship")
    confidence: float = Field(..., description="Confidence score for the suggestion")
    evidence: List[str] = Field(default_factory=list, description="Evidence supporting the suggestion")

class SuggestConnectionsCapability:
    """Capability for suggesting connections between entities in the knowledge graph."""
    
    def __init__(self, db: KnowledgeDB):
        self.db = db
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.rake = Rake()
        self.tfidf = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
        
        # Define domain-specific patterns and rules
        self.domain_patterns = {
            "technical": {
                "patterns": [
                    r"API|SDK|Framework|Library|Tool|Platform|Service",
                    r"Programming|Development|Engineering|Architecture",
                    r"Database|Storage|Cache|Queue|Stream|Pipeline"
                ],
                "relationship_types": ["USES", "INTEGRATES_WITH", "DEPENDS_ON"]
            },
            "business": {
                "patterns": [
                    r"Company|Organization|Business|Enterprise|Startup",
                    r"Market|Industry|Sector|Domain|Vertical",
                    r"Product|Service|Solution|Platform|Offering"
                ],
                "relationship_types": ["COMPETES_WITH", "PARTNERS_WITH", "ACQUIRED_BY"]
            },
            "academic": {
                "patterns": [
                    r"Research|Study|Paper|Publication|Thesis",
                    r"University|Institute|Laboratory|Department",
                    r"Field|Discipline|Domain|Area|Subject"
                ],
                "relationship_types": ["CITES", "REFERENCES", "BUILDS_UPON"]
            }
        }
    
    async def suggest_connections(
        self,
        entity_id: str,
        max_suggestions: int = 5,
        min_confidence: float = 0.5,
        relationship_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Suggest potential connections for an entity.
        
        Args:
            entity_id: ID of the entity to find connections for
            max_suggestions: Maximum number of suggestions to return
            min_confidence: Minimum confidence score for suggestions
            relationship_types: Optional list of relationship types to consider
            
        Returns:
            Dictionary containing suggested connections
        """
        try:
            # Get the entity's embedding and properties
            entity = await self._get_entity(entity_id)
            if not entity:
                return {"status": "error", "message": f"Entity {entity_id} not found"}
            
            # Get potential target entities
            target_entities = await self._get_potential_targets(
                entity,
                max_suggestions * 2,  # Get more than needed to filter
                relationship_types
            )
            
            # Score and rank potential connections
            suggestions = []
            for target in target_entities:
                # Calculate similarity score
                similarity = self._calculate_similarity(entity, target)
                
                # Determine relationship type based on entity types and content
                rel_type = self._infer_relationship_type(entity, target)
                
                # Generate evidence
                evidence = self._generate_evidence(entity, target, rel_type)
                
                # Calculate confidence score
                confidence = self._calculate_confidence(similarity, evidence)
                
                if confidence >= min_confidence:
                    suggestions.append(SuggestedConnection(
                        source_id=entity_id,
                        target_id=target["id"],
                        relationship_type=rel_type,
                        confidence=confidence,
                        evidence=evidence
                    ))
            
            # Sort by confidence and limit results
            suggestions.sort(key=lambda x: x.confidence, reverse=True)
            suggestions = suggestions[:max_suggestions]
            
            return {
                "status": "success",
                "entity_id": entity_id,
                "suggestions": [s.dict() for s in suggestions]
            }
            
        except Exception as e:
            logger.error(f"Error suggesting connections: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get an entity by ID."""
        try:
            response = requests.get(
                f"{self.db.supabase_url}/rest/v1/entities",
                headers=self.db.headers,
                params={"id": f"eq.{entity_id}"}
            )
            
            if response.status_code != 200:
                return None
                
            entities = response.json()
            return entities[0] if entities else None
            
        except Exception as e:
            logger.error(f"Error getting entity: {str(e)}")
            return None
    
    async def _get_potential_targets(
        self,
        source_entity: Dict[str, Any],
        limit: int,
        relationship_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get potential target entities for connection suggestions."""
        try:
            # Build query parameters
            params = {
                "limit": str(limit),
                "order": f"embedding <-> '{source_entity['embedding']}'::vector"
            }
            
            # Add relationship type filter if specified
            if relationship_types:
                params["type"] = f"in.({','.join(relationship_types)})"
            
            # Make the request
            response = requests.get(
                f"{self.db.supabase_url}/rest/v1/entities",
                headers=self.db.headers,
                params=params
            )
            
            if response.status_code != 200:
                return []
                
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting potential targets: {str(e)}")
            return []
    
    def _calculate_similarity(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> float:
        """Calculate similarity between two entities."""
        if not entity1.get("embedding") or not entity2.get("embedding"):
            return 0.0
            
        # Calculate cosine similarity between embeddings
        # This is a simplified version - in practice, you'd use a proper vector similarity function
        dot_product = sum(a * b for a, b in zip(entity1["embedding"], entity2["embedding"]))
        norm1 = sum(a * a for a in entity1["embedding"]) ** 0.5
        norm2 = sum(a * a for a in entity2["embedding"]) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
    
    def _infer_relationship_type(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any]
    ) -> str:
        """Infer the most likely relationship type between entities."""
        # This is a simplified version - in practice, you'd use more sophisticated logic
        source_type = source.get("type", "").lower()
        target_type = target.get("type", "").lower()
        
        # Define some basic relationship type rules
        type_rules = {
            ("person", "organization"): "WORKS_FOR",
            ("organization", "person"): "EMPLOYS",
            ("concept", "concept"): "RELATED_TO",
            ("document", "concept"): "DESCRIBES",
            ("concept", "document"): "DESCRIBED_BY"
        }
        
        # Check for exact matches
        key = (source_type, target_type)
        if key in type_rules:
            return type_rules[key]
            
        # Default to RELATED_TO if no specific rule matches
        return "RELATED_TO"
    
    def _analyze_text(self, text: str) -> Dict[str, Any]:
        """Perform comprehensive text analysis using multiple NLP techniques."""
        if not text:
            return {}
            
        # Basic text preprocessing
        text = text.lower()
        doc = nlp(text)
        
        # Extract named entities
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # Extract key phrases using RAKE
        self.rake.extract_keywords_from_text(text)
        key_phrases = self.rake.get_ranked_phrases()[:5]
        
        # Extract sentiment
        sentiment = TextBlob(text).sentiment
        
        # Extract POS tags and lemmas
        pos_tags = [(token.text, token.pos_) for token in doc]
        lemmas = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        
        # Extract dependency relationships
        dependencies = [(token.text, token.dep_, token.head.text) for token in doc]
        
        return {
            "entities": entities,
            "key_phrases": key_phrases,
            "sentiment": {
                "polarity": sentiment.polarity,
                "subjectivity": sentiment.subjectivity
            },
            "pos_tags": pos_tags,
            "lemmas": lemmas,
            "dependencies": dependencies
        }
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> Dict[str, float]:
        """Calculate multiple text similarity metrics."""
        if not text1 or not text2:
            return {"overall": 0.0}
            
        # Basic string similarity
        sequence_similarity = SequenceMatcher(None, text1, text2).ratio()
        
        # TF-IDF cosine similarity
        tfidf_matrix = self.tfidf.fit_transform([text1, text2])
        tfidf_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Semantic similarity using spaCy
        doc1 = nlp(text1)
        doc2 = nlp(text2)
        semantic_similarity = doc1.similarity(doc2)
        
        # Combine similarities with weights
        overall_similarity = (
            0.3 * sequence_similarity +
            0.4 * tfidf_similarity +
            0.3 * semantic_similarity
        )
        
        return {
            "overall": overall_similarity,
            "sequence": sequence_similarity,
            "tfidf": tfidf_similarity,
            "semantic": semantic_similarity
        }
    
    def _extract_key_terms(self, text: str) -> List[Tuple[str, float]]:
        """Extract key terms with importance scores."""
        if not text:
            return []
            
        # Use RAKE for keyword extraction
        self.rake.extract_keywords_from_text(text)
        key_terms = self.rake.get_ranked_phrases_with_scores()[:10]
        
        # Extract named entities
        doc = nlp(text)
        entities = [(ent.text, 1.0) for ent in doc.ents]
        
        # Combine and deduplicate
        all_terms = {}
        for term, score in key_terms + entities:
            term = term.lower()
            if term not in all_terms or score > all_terms[term]:
                all_terms[term] = score
        
        return sorted(all_terms.items(), key=lambda x: x[1], reverse=True)
    
    def _analyze_relationship_patterns(
        self,
        source_text: str,
        target_text: str
    ) -> List[Tuple[str, float]]:
        """Analyze potential relationship patterns between texts."""
        patterns = []
        
        # Combine texts for analysis
        combined_text = f"{source_text} {target_text}"
        doc = nlp(combined_text)
        
        # Look for relationship indicators
        for token in doc:
            if token.dep_ in ["nsubj", "dobj", "pobj"]:
                # Check for relationship verbs
                if token.head.pos_ == "VERB":
                    relationship = f"{token.head.lemma_}_{token.dep_}"
                    patterns.append((relationship, 0.8))
            
            # Check for prepositional relationships
            if token.pos_ == "ADP" and token.head.pos_ == "NOUN":
                relationship = f"{token.lemma_}_{token.head.lemma_}"
                patterns.append((relationship, 0.6))
        
        return patterns
    
    def _generate_evidence(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        relationship_type: str
    ) -> List[str]:
        """Generate detailed evidence supporting a suggested connection."""
        evidence = []
        
        # 1. Type-based evidence
        source_type = source.get("type", "").lower()
        target_type = target.get("type", "").lower()
        evidence.append(f"Entity types ({source_type} → {target_type}) suggest {relationship_type} relationship")
        
        # 2. Content-based evidence
        if source.get("content") and target.get("content"):
            source_text = source.get("content", "")
            target_text = target.get("content", "")
            
            # Perform comprehensive text analysis
            source_analysis = self._analyze_text(source_text)
            target_analysis = self._analyze_text(target_text)
            
            # Calculate multiple similarity metrics
            similarities = self._calculate_text_similarity(source_text, target_text)
            if similarities["overall"] > 0.3:
                evidence.append(
                    f"Text similarity scores - Overall: {similarities['overall']:.2f}, "
                    f"Sequence: {similarities['sequence']:.2f}, "
                    f"TF-IDF: {similarities['tfidf']:.2f}, "
                    f"Semantic: {similarities['semantic']:.2f}"
                )
            
            # Compare key terms
            source_terms = self._extract_key_terms(source_text)
            target_terms = self._extract_key_terms(target_text)
            common_terms = set(term for term, _ in source_terms) & set(term for term, _ in target_terms)
            if common_terms:
                evidence.append(f"Shared key terms: {', '.join(sorted(common_terms)[:5])}")
            
            # Analyze relationship patterns
            patterns = self._analyze_relationship_patterns(source_text, target_text)
            if patterns:
                evidence.append(
                    f"Detected relationship patterns: {', '.join(f'{p} ({s:.2f})' for p, s in patterns[:3])}"
                )
            
            # Compare named entities
            source_entities = set(e[0] for e in source_analysis.get("entities", []))
            target_entities = set(e[0] for e in target_analysis.get("entities", []))
            common_entities = source_entities & target_entities
            if common_entities:
                evidence.append(f"Shared named entities: {', '.join(sorted(common_entities))}")
        
        # 3. Property-based evidence
        if source.get("properties") and target.get("properties"):
            source_props = source["properties"]
            target_props = target["properties"]
            
            # Compare specific property values
            for prop in ["category", "domain", "tags", "keywords"]:
                if prop in source_props and prop in target_props:
                    source_val = source_props[prop]
                    target_val = target_props[prop]
                    if isinstance(source_val, list) and isinstance(target_val, list):
                        common = set(source_val) & set(target_val)
                        if common:
                            evidence.append(f"Shared {prop}: {', '.join(sorted(common))}")
                    elif source_val == target_val:
                        evidence.append(f"Matching {prop}: {source_val}")
        
        # 4. Domain-specific evidence
        domain = self._identify_domain(source, target)
        if domain:
            evidence.append(f"Domain context: {domain}")
            # Add domain-specific relationship evidence
            domain_evidence = self._generate_domain_evidence(source, target, domain)
            evidence.extend(domain_evidence)
        
        # 5. Temporal evidence (if available)
        if "created_at" in source and "created_at" in target:
            source_time = source["created_at"]
            target_time = target["created_at"]
            if source_time and target_time:
                evidence.append(f"Temporal relationship: {self._describe_temporal_relationship(source_time, target_time)}")
        
        # 6. Structural evidence
        if "metadata" in source and "metadata" in target:
            source_meta = source["metadata"]
            target_meta = target["metadata"]
            structural_evidence = self._analyze_structure(source_meta, target_meta)
            if structural_evidence:
                evidence.append(f"Structural relationship: {structural_evidence}")
        
        return evidence
    
    def _identify_domain(self, source: Dict[str, Any], target: Dict[str, Any]) -> Optional[str]:
        """Identify the domain context of the entities."""
        content = f"{source.get('content', '')} {target.get('content', '')}"
        for domain, patterns in self.domain_patterns.items():
            for pattern in patterns["patterns"]:
                if re.search(pattern, content, re.IGNORECASE):
                    return domain
        return None
    
    def _generate_domain_evidence(
        self,
        source: Dict[str, Any],
        target: Dict[str, Any],
        domain: str
    ) -> List[str]:
        """Generate domain-specific evidence."""
        evidence = []
        domain_info = self.domain_patterns[domain]
        
        # Check for domain-specific relationship types
        if "relationship_types" in domain_info:
            evidence.append(f"Domain-specific relationship types: {', '.join(domain_info['relationship_types'])}")
        
        # Add domain-specific patterns
        content = f"{source.get('content', '')} {target.get('content', '')}"
        for pattern in domain_info["patterns"]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                evidence.append(f"Domain-specific terms: {', '.join(set(matches))}")
        
        return evidence
    
    def _describe_temporal_relationship(self, time1: str, time2: str) -> str:
        """Describe the temporal relationship between two timestamps."""
        # This is a simplified version - in practice, you'd parse the timestamps
        # and calculate the actual time difference
        return "concurrent"  # Placeholder
    
    def _analyze_structure(self, meta1: Dict[str, Any], meta2: Dict[str, Any]) -> Optional[str]:
        """Analyze structural relationships between entities."""
        # Check for hierarchical relationships
        if "parent_id" in meta1 and meta1["parent_id"] == meta2.get("id"):
            return "parent-child relationship"
        if "parent_id" in meta2 and meta2["parent_id"] == meta1.get("id"):
            return "child-parent relationship"
        
        # Check for sibling relationships
        if "parent_id" in meta1 and "parent_id" in meta2 and meta1["parent_id"] == meta2["parent_id"]:
            return "sibling relationship"
        
        return None
    
    def _calculate_confidence(
        self,
        similarity: float,
        evidence: List[str]
    ) -> float:
        """Calculate confidence score for a suggested connection."""
        # Base confidence on similarity
        confidence = similarity
        
        # Boost confidence based on evidence
        evidence_boost = min(len(evidence) * 0.1, 0.3)  # Max 0.3 boost from evidence
        confidence += evidence_boost
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence)) 
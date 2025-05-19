"""
Document Processing Agent
Integrates Intelligent PDF Pipeline with Meepzorp's agent framework
"""
import os
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from pydantic import BaseModel
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from supabase import create_client, Client
import tempfile
import uuid

# === Agent Configuration ===
AGENT_NAME = "document_processor"
AGENT_VERSION = "1.0.0"
AGENT_CAPABILITIES = [
    "pdf_processing",
    "document_analysis",
    "semantic_search",
    "summarization",
    "creative_concepts"
]

# === FastAPI App Factory ===
def create_app():
    app = FastAPI(title=f"Meepzorp {AGENT_NAME.title()} Agent")
    
    # Initialize Supabase client
    supabase: Client = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

    # === Pydantic Models ===
    class ProcessingContext(BaseModel):
        user_id: str
        project_id: str
        workflow_id: Optional[str] = None

    class SummarizeRequest(BaseModel):
        document_id: str
        query: Optional[str] = None

    # === Helper Functions ===
    def get_vector_store():
        return SupabaseVectorStore(
            client=supabase,
            embedding=OpenAIEmbeddings(),
            table_name="document_chunks",
            query_name="match_documents"
        )

    def get_retriever(top_k: int = 5):
        return get_vector_store().as_retriever(search_kwargs={"k": top_k})

    # === Agent Registration ===
    @app.on_event("startup")
    async def register_agent():
        supabase.table("agent_registry").upsert({
            "name": AGENT_NAME,
            "version": AGENT_VERSION,
            "capabilities": AGENT_CAPABILITIES,
            "status": "active",
            "endpoint": f"http://{AGENT_NAME}:8000"
        }).execute()

    # === Document Processing Endpoints ===
    @app.post("/process")
    async def process_document(
        file: UploadFile = File(...),
        context: Optional[ProcessingContext] = None
    ):
        """Process a document and store its contents in the knowledge base"""
        try:
            # Save uploaded file temporarily
            content = await file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            # Process document
            loader = PyPDFLoader(tmp_path)
            pages = loader.load()
            
            # Enhanced chunking with semantic awareness
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
                length_function=len
            )
            chunks = text_splitter.split_documents(pages)

            # Generate document ID and metadata
            doc_id = str(uuid.uuid4())
            metadata = {
                "id": doc_id,
                "title": file.filename,
                "source": "uploaded",
                "type": "pdf",
                "chunks": len(chunks)
            }

            if context:
                metadata.update({
                    "user_id": context.user_id,
                    "project_id": context.project_id,
                    "workflow_id": context.workflow_id
                })

            # Store document metadata
            supabase.table("documents").insert(metadata).execute()

            # Store chunks with embeddings
            texts = [chunk.page_content for chunk in chunks]
            chunk_metadata = [{
                "document_id": doc_id,
                "chunk_index": i,
                "page_num": chunks[i].metadata.get("page", 0)
            } for i in range(len(chunks))]

            get_vector_store().add_texts(texts, metadatas=chunk_metadata)

            # Cleanup
            os.remove(tmp_path)

            return {
                "status": "success",
                "document_id": doc_id,
                "chunks_processed": len(chunks)
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/summarize")
    async def summarize_document(request: SummarizeRequest):
        """Generate a summary of the document with cited sources"""
        try:
            # Get relevant chunks
            query = request.query or "Summarize the key points of this document"
            docs = get_retriever().get_relevant_documents(query)
            
            if not docs:
                raise HTTPException(status_code=404, detail="No relevant content found")

            # Prepare context with citations
            context = "\n\n".join([
                f"{doc.page_content} [chunk:{doc.metadata['chunk_index']}, page:{doc.metadata['page_num']}]"
                for doc in docs
            ])

            # Generate summary
            prompt = PromptTemplate(
                input_variables=["context", "query"],
                template="""
You are a strategic research analyst. Based on the following content (with citations), provide a comprehensive summary.
Include citations [chunk:X, page:Y] when referencing specific information.

Content:
{context}

Query:
{query}

Provide a structured summary with citations:"""
            )

            summary_chain = LLMChain(
                llm=ChatOpenAI(model_name="gpt-4-turbo", temperature=0.3),
                prompt=prompt
            )

            summary = summary_chain.run({
                "context": context,
                "query": query
            })

            # Store summary
            summary_id = str(uuid.uuid4())
            supabase.table("summaries").insert({
                "id": summary_id,
                "document_id": request.document_id,
                "query": query,
                "summary": summary,
                "source_chunks": len(docs)
            }).execute()

            return {
                "summary_id": summary_id,
                "summary": summary,
                "source_count": len(docs)
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/retrieve")
    async def retrieve_content(
        query: str,
        document_id: Optional[str] = None,
        limit: int = 5
    ):
        """Retrieve relevant document chunks for a query"""
        try:
            retriever = get_retriever(top_k=limit)
            docs = retriever.get_relevant_documents(query)
            
            return {
                "results": [{
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": doc.metadata.get("score", None)
                } for doc in docs]
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/health")
    async def health_check():
        """Agent health check endpoint"""
        try:
            # Verify Supabase connection
            supabase.table("documents").select("id").limit(1).execute()
            return {"status": "healthy", "agent": AGENT_NAME, "version": AGENT_VERSION}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    return app

# Create the application instance
app = create_app() 
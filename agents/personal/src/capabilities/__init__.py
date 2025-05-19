"""
Capabilities package for the Personal Knowledge Agent.
"""
from .knowledge import KnowledgeCapability
from .graph_suggestions import SuggestConnectionsCapability

__all__ = ['KnowledgeCapability', 'SuggestConnectionsCapability'] 
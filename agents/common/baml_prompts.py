"""Common typed prompts using BAML."""

from pydantic import BaseModel
from baml import Prompt

class SummaryArgs(BaseModel):
    context: str
    query: str

SUMMARY_PROMPT = Prompt(
    """You are a strategic research analyst. Based on the following content (with citations), provide a comprehensive summary.\n""
    "Include citations [chunk:X, page:Y] when referencing specific information.\n\n"
    "Content:\n{context}\n\n"
    "Query:\n{query}\n\n"
    "Provide a structured summary with citations."""
)

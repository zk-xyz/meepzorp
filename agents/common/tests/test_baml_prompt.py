import pytest
from agents.common.llm import LLMService
from agents.common.baml_prompts import SUMMARY_PROMPT, SummaryArgs


def test_baml_prompt_render():
    service = LLMService()
    chain = service.create_chain(
        prompt_template="",
        input_variables=[],
        baml_prompt=SUMMARY_PROMPT,
    )
    rendered = chain.prompt.format(**SummaryArgs(context="ctx", query="q").model_dump())
    assert "ctx" in rendered and "q" in rendered

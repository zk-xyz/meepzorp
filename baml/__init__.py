from __future__ import annotations
from string import Formatter
from langchain_core.prompts import PromptTemplate

class Prompt:
    """Minimal BAML-like prompt for testing purposes."""

    def __init__(self, template: str):
        self.template = template
        self.input_variables = [f for _, f, _, _ in Formatter().parse(template) if f]

    def format(self, **kwargs) -> str:
        return self.template.format(**kwargs)

    def to_langchain(self) -> PromptTemplate:
        return PromptTemplate(template=self.template, input_variables=self.input_variables)

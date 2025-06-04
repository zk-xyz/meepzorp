"""
LLM integration module using LangChain.

This module provides a unified interface for agents to use multiple LLM providers
through LangChain, with support for different models and configurations.
"""
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseLLM, BaseChatModel
from langchain_core.callbacks import CallbackManager
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.conversation.base import ConversationChain
from langchain.memory.buffer import ConversationBufferMemory
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class LLMConfig(BaseModel):
    """Configuration for LLM providers."""
    provider: str = Field(..., description="LLM provider (openai, anthropic)")
    model: str = Field(..., description="Model name")
    temperature: float = Field(0.7, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    streaming: bool = Field(False, description="Whether to stream responses")

class LLMService:
    """Service for managing LLM interactions."""
    
    def __init__(self, default_config: Optional[LLMConfig] = None):
        """
        Initialize the LLM service.
        
        Args:
            default_config: Default LLM configuration
        """
        self.default_config = default_config or LLMConfig(
            provider="openai",  # Default provider
            model="gpt-4",  # Default model
            temperature=float(os.getenv("DEFAULT_LLM_TEMPERATURE", "0.7")),
            streaming=os.getenv("DEFAULT_LLM_STREAMING", "false").lower() == "true"
        )
        self.llm = self._create_llm(self.default_config)
        self.conversations: Dict[str, ConversationChain] = {}
    
    def _create_llm(self, config: LLMConfig) -> Union[BaseChatModel, BaseLLM]:
        """Create an LLM instance based on configuration."""
        handlers = []
        if config.streaming:
            handlers.append(StreamingStdOutCallbackHandler())
        
        if config.provider.lower() == "openai":
            if config.model.startswith("gpt"):
                return ChatOpenAI(
                    model_name=config.model,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    streaming=config.streaming,
                    callbacks=handlers
                )
        elif config.provider.lower() == "anthropic":
            if config.model.startswith("claude"):
                return ChatAnthropic(
                    model=config.model,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    streaming=config.streaming,
                    callbacks=handlers
                )
        
        raise ValueError(f"Unsupported LLM provider or model: {config.provider} - {config.model}")
    
    def create_chain(
        self,
        prompt_template: str,
        input_variables: List[str],
        memory: bool = False,
        baml_prompt: Optional[Any] = None
    ) -> LLMChain:
        """
        Create a chain with the given prompt template.
        
        Args:
            prompt_template: Template for the prompt
            input_variables: Variables to be filled in the template
            memory: Whether to include conversation memory
            
        Returns:
            An LLM chain
        """
        if baml_prompt is not None:
            prompt = baml_prompt.to_langchain()
        else:
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=input_variables
            )

        if memory:
            memory = ConversationBufferMemory()
            return ConversationChain(
                llm=self.llm,
                memory=memory,
                prompt=prompt if baml_prompt else ChatPromptTemplate.from_template(prompt_template)
            )
        return LLMChain(
            llm=self.llm,
            prompt=prompt
        )
    
    async def generate(
        self,
        prompt: str,
        conversation_id: Optional[str] = None,
        config: Optional[LLMConfig] = None
    ) -> str:
        """
        Generate a response using the LLM.
        
        Args:
            prompt: Input prompt
            conversation_id: Optional conversation ID for context
            config: Optional LLM configuration override
            
        Returns:
            Generated response
        """
        try:
            if conversation_id:
                if conversation_id not in self.conversations:
                    self.conversations[conversation_id] = ConversationChain(
                        llm=self.llm,
                        memory=ConversationBufferMemory()
                    )
                chain = self.conversations[conversation_id]
                response = await chain.arun(prompt)
            else:
                if config:
                    llm = self._create_llm(config)
                else:
                    llm = self.llm
                response = await llm.agenerate([prompt])
                response = response.generations[0][0].text
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise 
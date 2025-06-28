"""
Models package for Typify application.
Contains LLM interfaces and implementations.
"""

from .llm_interface import (
    ILLMProvider,
    IGrammarCorrector,
    ITextSummarizer,
    IToneChanger,
    ITextProcessor,
    TextProcessingResult
)

from .llama_provider import (
    LlamaCppProvider,
    ModelDownloader,
    create_llm_provider
)

__all__ = [
    # Interfaces
    'ILLMProvider',
    'IGrammarCorrector', 
    'ITextSummarizer',
    'IToneChanger',
    'ITextProcessor',
    'TextProcessingResult',
    
    # Implementations
    'LlamaCppProvider',
    'ModelDownloader',
    'create_llm_provider',
] 
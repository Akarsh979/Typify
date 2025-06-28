"""
Abstract interface for LLM operations.
Follows the Interface Segregation and Dependency Inversion principles.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TextProcessingResult:
    """Result of a text processing operation."""
    processed_text: str
    original_text: str
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ITextProcessor(ABC):
    """Abstract interface for text processing operations."""
    
    @abstractmethod
    def process_text(self, text: str, **kwargs) -> TextProcessingResult:
        """Process text and return the result."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the processor is available and ready."""
        pass


class IGrammarCorrector(ITextProcessor):
    """Interface for grammar correction."""
    
    @abstractmethod
    def fix_grammar(self, text: str) -> TextProcessingResult:
        """Fix grammar errors in the text."""
        pass


class ITextSummarizer(ITextProcessor):
    """Interface for text summarization."""
    
    @abstractmethod
    def summarize(self, text: str) -> TextProcessingResult:
        """Summarize the given text."""
        pass


class IToneChanger(ITextProcessor):
    """Interface for tone modification."""
    
    @abstractmethod
    def change_tone(self, text: str, target_tone: str = "formal") -> TextProcessingResult:
        """Change the tone of the text."""
        pass


class ILLMProvider(ABC):
    """Abstract interface for LLM providers."""
    
    @abstractmethod
    def generate_response(
        self, 
        prompt: str, 
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
        stop_tokens: list,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if the model is loaded and ready."""
        pass
    
    @abstractmethod
    def load_model(self) -> bool:
        """Load the model. Returns True if successful."""
        pass 
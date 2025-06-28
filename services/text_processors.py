"""
Concrete implementations of text processing services.
Each processor has a single responsibility and uses dependency injection.
"""
import time
import logging
from string import Template
from typing import Optional

from models.llm_interface import (
    IGrammarCorrector, ITextSummarizer, IToneChanger,
    ILLMProvider, TextProcessingResult
)
from services.cache_service import CacheService, get_cache_service
from config import get_config


logger = logging.getLogger(__name__)


class PromptTemplates:
    """Centralized prompt templates."""
    
    GRAMMAR_CORRECTION = Template(
        """[INST] Fix all typos, grammar, and punctuation errors in the following text. Keep the same meaning and preserve line breaks. Only return the corrected text without any explanations.

Text to fix: $text [/INST]"""
    )
    
    SUMMARIZATION = Template(
        """[INST] Summarize the following text in a concise and clear manner. Keep the main points and key information. Make it about 1/3 the length of the original. Only return the summarized text without any explanations.

Text to summarize: $text [/INST]"""
    )
    
    TONE_CHANGE = Template(
        """[INST] Rewrite the following text to make it more formal and professional while keeping the same meaning. Use appropriate business language and tone. Only return the formal text without any explanations.

Text to make formal: $text [/INST]"""
    )


class BaseTextProcessor:
    """Base class for text processors with common functionality."""
    
    def __init__(self, llm_provider: ILLMProvider, cache_service: Optional[CacheService] = None):
        self.llm_provider = llm_provider
        self.cache_service = cache_service or get_cache_service()
        self.config = get_config()
    
    def is_available(self) -> bool:
        """Check if the processor is available."""
        return self.llm_provider.is_loaded()
    
    def _validate_input(self, text: str) -> bool:
        """Validate input text."""
        return bool(text and text.strip())
    
    def _create_error_result(self, text: str, error_message: str) -> TextProcessingResult:
        """Create an error result."""
        return TextProcessingResult(
            processed_text=text,
            original_text=text,
            processing_time=0.0,
            success=False,
            error_message=error_message
        )


class GrammarCorrector(BaseTextProcessor, IGrammarCorrector):
    """Grammar correction processor."""
    
    def process_text(self, text: str, **kwargs) -> TextProcessingResult:
        """Process text for grammar correction."""
        return self.fix_grammar(text)
    
    def fix_grammar(self, text: str) -> TextProcessingResult:
        """Fix grammar errors in the text."""
        if not self._validate_input(text):
            return self._create_error_result(text, "Invalid input text")
        
        if not self.is_available():
            return self._create_error_result(text, "Grammar corrector not available")
        
        # Check cache first
        cached_result = self.cache_service.get_grammar_correction(text)
        if cached_result:
            return TextProcessingResult(
                processed_text=cached_result,
                original_text=text,
                processing_time=0.0,
                success=True,
                metadata={'from_cache': True}
            )
        
        try:
            start_time = time.time()
            
            prompt = PromptTemplates.GRAMMAR_CORRECTION.substitute(text=text)
            gen_config = self.config.generation
            
            response = self.llm_provider.generate_response(
                prompt=prompt,
                max_tokens=max(gen_config.grammar_min_tokens, len(text) * gen_config.grammar_max_tokens_multiplier),
                temperature=gen_config.grammar_temperature,
                top_p=gen_config.grammar_top_p,
                top_k=gen_config.grammar_top_k,
                stop_tokens=self.config.stop_tokens['default'],
                repeat_penalty=gen_config.grammar_repeat_penalty
            )
            
            processing_time = time.time() - start_time
            
            if not response['success']:
                return self._create_error_result(text, response['error'])
            
            corrected_text = response['response']['choices'][0]['text'].strip()
            
            # Validate response
            if not corrected_text or len(corrected_text) < len(text) * 0.3:
                return self._create_error_result(text, "Invalid response from model")
            
            # Cache the result
            self.cache_service.cache_grammar_correction(text, corrected_text)
            
            logger.info(f"Grammar correction took: {processing_time:.2f} seconds")
            
            return TextProcessingResult(
                processed_text=corrected_text,
                original_text=text,
                processing_time=processing_time,
                success=True,
                metadata={'from_cache': False}
            )
            
        except Exception as e:
            logger.error(f"Error in grammar correction: {e}")
            return self._create_error_result(text, str(e))


class TextSummarizer(BaseTextProcessor, ITextSummarizer):
    """Text summarization processor."""
    
    def process_text(self, text: str, **kwargs) -> TextProcessingResult:
        """Process text for summarization."""
        return self.summarize(text)
    
    def summarize(self, text: str) -> TextProcessingResult:
        """Summarize the given text."""
        if not self._validate_input(text):
            return self._create_error_result(text, "Invalid input text")
        
        if not self.is_available():
            return self._create_error_result(text, "Text summarizer not available")
        
        # Check cache first
        cached_result = self.cache_service.get_summary(text)
        if cached_result:
            return TextProcessingResult(
                processed_text=cached_result,
                original_text=text,
                processing_time=0.0,
                success=True,
                metadata={'from_cache': True}
            )
        
        try:
            start_time = time.time()
            
            prompt = PromptTemplates.SUMMARIZATION.substitute(text=text)
            gen_config = self.config.generation
            
            response = self.llm_provider.generate_response(
                prompt=prompt,
                max_tokens=min(gen_config.summary_max_tokens, max(gen_config.summary_min_tokens, len(text))),
                temperature=gen_config.summary_temperature,
                top_p=gen_config.summary_top_p,
                top_k=gen_config.summary_top_k,
                stop_tokens=self.config.stop_tokens['summarize'],
                repeat_penalty=gen_config.summary_repeat_penalty
            )
            
            processing_time = time.time() - start_time
            
            if not response['success']:
                return self._create_error_result(text, response['error'])
            
            summary_text = response['response']['choices'][0]['text'].strip()
            
            # Validate response
            if not summary_text:
                return self._create_error_result(text, "Empty summary response")
            
            # Cache the result
            self.cache_service.cache_summary(text, summary_text)
            
            logger.info(f"Summarization took: {processing_time:.2f} seconds")
            
            return TextProcessingResult(
                processed_text=summary_text,
                original_text=text,
                processing_time=processing_time,
                success=True,
                metadata={'from_cache': False}
            )
            
        except Exception as e:
            logger.error(f"Error in summarization: {e}")
            return self._create_error_result(text, str(e))


class ToneChanger(BaseTextProcessor, IToneChanger):
    """Tone modification processor."""
    
    def process_text(self, text: str, **kwargs) -> TextProcessingResult:
        """Process text for tone change."""
        target_tone = kwargs.get('target_tone', 'formal')
        return self.change_tone(text, target_tone)
    
    def change_tone(self, text: str, target_tone: str = "formal") -> TextProcessingResult:
        """Change the tone of the text."""
        if not self._validate_input(text):
            return self._create_error_result(text, "Invalid input text")
        
        if not self.is_available():
            return self._create_error_result(text, "Tone changer not available")
        
        # Check cache first
        cached_result = self.cache_service.get_tone_change(text, target_tone)
        if cached_result:
            return TextProcessingResult(
                processed_text=cached_result,
                original_text=text,
                processing_time=0.0,
                success=True,
                metadata={'from_cache': True, 'target_tone': target_tone}
            )
        
        try:
            start_time = time.time()
            
            # For now, only support formal tone
            if target_tone.lower() != 'formal':
                return self._create_error_result(text, f"Unsupported tone: {target_tone}")
            
            prompt = PromptTemplates.TONE_CHANGE.substitute(text=text)
            gen_config = self.config.generation
            
            response = self.llm_provider.generate_response(
                prompt=prompt,
                max_tokens=max(gen_config.tone_min_tokens, len(text) * gen_config.tone_max_tokens_multiplier),
                temperature=gen_config.tone_temperature,
                top_p=gen_config.tone_top_p,
                top_k=gen_config.tone_top_k,
                stop_tokens=self.config.stop_tokens['tone_change'],
                repeat_penalty=gen_config.tone_repeat_penalty
            )
            
            processing_time = time.time() - start_time
            
            if not response['success']:
                return self._create_error_result(text, response['error'])
            
            formal_text = response['response']['choices'][0]['text'].strip()
            
            # Validate response
            if not formal_text or len(formal_text) < len(text) * 0.3:
                return self._create_error_result(text, "Invalid tone change response")
            
            # Cache the result
            self.cache_service.cache_tone_change(text, formal_text, target_tone)
            
            logger.info(f"Tone change took: {processing_time:.2f} seconds")
            
            return TextProcessingResult(
                processed_text=formal_text,
                original_text=text,
                processing_time=processing_time,
                success=True,
                metadata={'from_cache': False, 'target_tone': target_tone}
            )
            
        except Exception as e:
            logger.error(f"Error in tone change: {e}")
            return self._create_error_result(text, str(e)) 
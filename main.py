"""
Main application module for Typify.
Implements dependency injection and follows SOLID principles.
"""
import os
import sys
from typing import Optional

# Setup environment before importing other modules
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from config import get_config
from logging_config import setup_logging, get_logger
from models.llama_provider import create_llm_provider, LlamaCppProvider
from models.llm_interface import ILLMProvider
from services.cache_service import get_cache_service, CacheService
from services.clipboard_service import get_clipboard_service, ClipboardService
from services.hotkey_service import get_hotkey_service, DefaultHotkeyHandlers, HotkeyService
from services.text_processors import GrammarCorrector, TextSummarizer, ToneChanger


class GrammarCloneApplication:
    """Main application class that orchestrates all services."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)
        
        # Services (initialized in _initialize_services)
        self.llm_provider: Optional[ILLMProvider] = None
        self.cache_service: Optional[CacheService] = None
        self.clipboard_service: Optional[ClipboardService] = None
        self.hotkey_service: Optional[HotkeyService] = None
        
        # Text processors (initialized in _initialize_text_processors)
        self.grammar_corrector: Optional[GrammarCorrector] = None
        self.text_summarizer: Optional[TextSummarizer] = None
        self.tone_changer: Optional[ToneChanger] = None
        
        # Hotkey handlers (initialized in _initialize_hotkey_handlers)
        self.hotkey_handlers: Optional[DefaultHotkeyHandlers] = None
        
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize all application services."""
        try:
            self.logger.info("Initializing Typify application...")
            
            # Initialize services
            self._initialize_services()
            
            # Initialize text processors
            self._initialize_text_processors()
            
            # Initialize hotkey handlers
            self._initialize_hotkey_handlers()
            
            # Setup hotkeys
            self._setup_hotkeys()
            
            self._initialized = True
            self.logger.info("Application initialized successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application: {e}")
            return False
    
    def _initialize_services(self) -> None:
        """Initialize core services."""
        self.logger.info("Initializing core services...")
        
        # Initialize LLM provider
        self.llm_provider = create_llm_provider()
        
        # Initialize services
        self.cache_service = get_cache_service()
        self.clipboard_service = get_clipboard_service()
        self.hotkey_service = get_hotkey_service()
        
        self.logger.info("Core services initialized")
    
    def _initialize_text_processors(self) -> None:
        """Initialize text processing services."""
        self.logger.info("Initializing text processors...")
        
        # Ensure services are initialized
        if self.llm_provider is None or self.cache_service is None:
            raise RuntimeError("Services must be initialized before text processors")
        
        # Create text processors with dependency injection
        self.grammar_corrector = GrammarCorrector(
            llm_provider=self.llm_provider,
            cache_service=self.cache_service
        )
        
        self.text_summarizer = TextSummarizer(
            llm_provider=self.llm_provider,
            cache_service=self.cache_service
        )
        
        self.tone_changer = ToneChanger(
            llm_provider=self.llm_provider,
            cache_service=self.cache_service
        )
        
        # Log availability status
        processors = [
            ("Grammar Corrector", self.grammar_corrector),
            ("Text Summarizer", self.text_summarizer),
            ("Tone Changer", self.tone_changer)
        ]
        
        for name, processor in processors:
            status = "available" if processor.is_available() else "not available"
            self.logger.info(f"{name}: {status}")
    
    def _initialize_hotkey_handlers(self) -> None:
        """Initialize hotkey handlers."""
        self.logger.info("Initializing hotkey handlers...")
        
        # Ensure text processors and clipboard service are initialized
        if (self.grammar_corrector is None or self.text_summarizer is None or 
            self.tone_changer is None or self.clipboard_service is None):
            raise RuntimeError("Text processors and clipboard service must be initialized before hotkey handlers")
        
        self.hotkey_handlers = DefaultHotkeyHandlers(
            grammar_corrector=self.grammar_corrector,
            text_summarizer=self.text_summarizer,
            tone_changer=self.tone_changer,
            clipboard_service=self.clipboard_service
        )
        
        self.logger.info("Hotkey handlers initialized")
    
    def _setup_hotkeys(self) -> None:
        """Setup global hotkeys."""
        self.logger.info("Setting up global hotkeys...")
        
        # Ensure hotkey service and handlers are initialized
        if self.hotkey_service is None or self.hotkey_handlers is None:
            raise RuntimeError("Hotkey service and handlers must be initialized before setup")
        
        # Register default handlers
        self.hotkey_service.register_default_handlers(
            self.hotkey_handlers.get_handlers()
        )
        
        # Start listening for hotkeys
        self.hotkey_service.start_listening()
        
        self.logger.info("Global hotkeys setup complete")
    
    def run(self) -> None:
        """Run the main application loop."""
        if not self._initialized:
            self.logger.error("Application not initialized. Call initialize() first.")
            return
        
        # Ensure hotkey service is available
        if self.hotkey_service is None:
            self.logger.error("Hotkey service not initialized. Cannot run application.")
            return
        
        try:
            self.logger.info("Typify is now running!")
            self.logger.info("Available hotkeys:")
            self.logger.info("  F9  - Fix grammar for current line")
            self.logger.info("  F10 - Fix grammar for selected text")
            self.logger.info("  F8  - Summarize selected text")
            self.logger.info("  F7  - Change tone to formal")
            self.logger.info("  Ctrl+Shift+E - Exit application")
            
            # Wait for hotkey events (blocking)
            self.hotkey_service.wait_for_hotkeys()
            
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Shutdown the application gracefully."""
        self.logger.info("Shutting down application...")
        
        try:
            if self.hotkey_service:
                self.hotkey_service.stop_listening()
            
            # Clear caches
            if self.cache_service:
                stats = self.cache_service.get_cache_stats()
                self.logger.info(f"Cache statistics: {stats}")
            
            self.logger.info("Application shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def get_status(self) -> dict:
        """Get application status information."""
        return {
            'initialized': self._initialized,
            'llm_available': self.llm_provider.is_loaded() if self.llm_provider else False,
            'grammar_corrector_available': self.grammar_corrector.is_available() if self.grammar_corrector else False,
            'text_summarizer_available': self.text_summarizer.is_available() if self.text_summarizer else False,
            'tone_changer_available': self.tone_changer.is_available() if self.tone_changer else False,
            'cache_stats': self.cache_service.get_cache_stats() if self.cache_service else None,
        }


def main():
    """Main entry point of the application."""
    # Setup logging
    setup_logging(
        level="INFO",
        log_to_file=True,
        console_format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger = get_logger(__name__)
    logger.info("Starting Typify application...")
    
    try:
        # Create and initialize application
        app = GrammarCloneApplication()
        
        if not app.initialize():
            logger.error("Failed to initialize application")
            sys.exit(1)
        
        # Run the application
        app.run()
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
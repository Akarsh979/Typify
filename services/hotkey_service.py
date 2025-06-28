"""
Hotkey service for managing global keyboard shortcuts.
Follows the Open/Closed Principle by allowing easy extension of hotkeys.
"""
import sys
import logging
from typing import Dict, Callable, Protocol
from pynput import keyboard

from config import get_config


logger = logging.getLogger(__name__)


class HotkeyHandler(Protocol):
    """Protocol for hotkey handlers."""
    
    def __call__(self) -> None:
        """Handle the hotkey press."""
        pass


class HotkeyService:
    """Service for managing global hotkeys."""
    
    def __init__(self):
        self.config = get_config()
        self.handlers: Dict[str, HotkeyHandler] = {}
        self.hotkey_listener = None
    
    def register_handler(self, hotkey: str, handler: HotkeyHandler) -> None:
        """Register a hotkey handler."""
        self.handlers[hotkey] = handler
        logger.info(f"Registered hotkey handler: {hotkey}")
    
    def unregister_handler(self, hotkey: str) -> None:
        """Unregister a hotkey handler."""
        if hotkey in self.handlers:
            del self.handlers[hotkey]
            logger.info(f"Unregistered hotkey handler: {hotkey}")
    
    def start_listening(self) -> None:
        """Start listening for global hotkeys."""
        try:
            if self.hotkey_listener is not None:
                logger.warning("Hotkey listener already running")
                return
            
            logger.info("Starting hotkey listener...")
            logger.info("Available hotkeys:")
            for hotkey in self.handlers.keys():
                logger.info(f"  {hotkey}")
            
            self.hotkey_listener = keyboard.GlobalHotKeys(self.handlers)
            self.hotkey_listener.start()
            
            logger.info("Hotkey listener started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start hotkey listener: {e}")
            raise
    
    def stop_listening(self) -> None:
        """Stop listening for global hotkeys."""
        if self.hotkey_listener is not None:
            self.hotkey_listener.stop()
            self.hotkey_listener = None
            logger.info("Hotkey listener stopped")
    
    def wait_for_hotkeys(self) -> None:
        """Block and wait for hotkey events."""
        if self.hotkey_listener is None:
            logger.error("Hotkey listener not started")
            return
        
        try:
            self.hotkey_listener.join()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            self.stop_listening()
    
    def register_default_handlers(self, handlers: Dict[str, HotkeyHandler]) -> None:
        """Register default application handlers."""
        hotkey_config = self.config.hotkeys
        
        # Map configuration keys to handlers
        hotkey_mapping = {
            hotkey_config.grammar_fix_line: handlers.get('grammar_fix_line'),
            hotkey_config.grammar_fix_selection: handlers.get('grammar_fix_selection'),
            hotkey_config.summarize: handlers.get('summarize'),
            hotkey_config.change_tone: handlers.get('change_tone'),
            hotkey_config.exit_app: handlers.get('exit_app'),
        }
        
        # Register valid handlers
        for hotkey, handler in hotkey_mapping.items():
            if handler is not None:
                self.register_handler(hotkey, handler)
            else:
                logger.warning(f"No handler provided for hotkey: {hotkey}")


class DefaultHotkeyHandlers:
    """Default hotkey handlers for the application."""
    
    def __init__(self, 
                 grammar_corrector=None,
                 text_summarizer=None,
                 tone_changer=None,
                 clipboard_service=None):
        self.grammar_corrector = grammar_corrector
        self.text_summarizer = text_summarizer
        self.tone_changer = tone_changer
        self.clipboard_service = clipboard_service
    
    def grammar_fix_line(self) -> None:
        """Handle F9 - Fix grammar for current line."""
        try:
            logger.info("F9 pressed - Fixing current line grammar")
            
            if not self.grammar_corrector or not self.clipboard_service:
                logger.error("Grammar corrector or clipboard service not available")
                return
            
            # Get current line text
            text = self.clipboard_service.copy_current_line()
            if not text.strip():
                logger.warning("No text found on current line")
                return
            
            # Process text
            result = self.grammar_corrector.fix_grammar(text)
            
            if result.success:
                # Replace current line with corrected text
                self.clipboard_service.replace_current_line_with_text(result.processed_text)
                
                # Log timing information
                if result.metadata and result.metadata.get('from_cache'):
                    logger.info("Used cached result")
                else:
                    logger.info(f"Grammar correction took: {result.processing_time:.2f} seconds")
            else:
                logger.error(f"Grammar correction failed: {result.error_message}")
                
        except Exception as e:
            logger.error(f"Error in grammar_fix_line: {e}")
    
    def grammar_fix_selection(self) -> None:
        """Handle F10 - Fix grammar for selected text."""
        try:
            logger.info("F10 pressed - Fixing selected text grammar")
            
            if not self.grammar_corrector or not self.clipboard_service:
                logger.error("Grammar corrector or clipboard service not available")
                return
            
            # Get selected text
            text = self.clipboard_service.copy_selection()
            if not text.strip():
                logger.warning("No text selected")
                return
            
            # Process text
            result = self.grammar_corrector.fix_grammar(text)
            
            if result.success:
                # Replace selection with corrected text
                self.clipboard_service.replace_selection_with_text(result.processed_text)
                
                # Log timing information
                if result.metadata and result.metadata.get('from_cache'):
                    logger.info("Used cached result")
                else:
                    logger.info(f"Grammar correction took: {result.processing_time:.2f} seconds")
            else:
                logger.error(f"Grammar correction failed: {result.error_message}")
                
        except Exception as e:
            logger.error(f"Error in grammar_fix_selection: {e}")
    
    def summarize(self) -> None:
        """Handle F8 - Summarize selected text."""
        try:
            logger.info("F8 pressed - Summarizing selected text")
            
            if not self.text_summarizer or not self.clipboard_service:
                logger.error("Text summarizer or clipboard service not available")
                return
            
            # Get selected text
            text = self.clipboard_service.copy_selection()
            if not text.strip():
                logger.warning("No text selected")
                return
            
            # Process text
            result = self.text_summarizer.summarize(text)
            
            if result.success:
                # Replace selection with summary
                self.clipboard_service.replace_selection_with_text(result.processed_text)
                
                # Log timing information
                if result.metadata and result.metadata.get('from_cache'):
                    logger.info("Used cached result")
                else:
                    logger.info(f"Summarization took: {result.processing_time:.2f} seconds")
            else:
                logger.error(f"Summarization failed: {result.error_message}")
                
        except Exception as e:
            logger.error(f"Error in summarize: {e}")
    
    def change_tone(self) -> None:
        """Handle F7 - Change tone to formal."""
        try:
            logger.info("F7 pressed - Changing tone to formal")
            
            if not self.tone_changer or not self.clipboard_service:
                logger.error("Tone changer or clipboard service not available")
                return
            
            # Get selected text
            text = self.clipboard_service.copy_selection()
            if not text.strip():
                logger.warning("No text selected")
                return
            
            # Process text
            result = self.tone_changer.change_tone(text, "formal")
            
            if result.success:
                # Replace selection with formal text
                self.clipboard_service.replace_selection_with_text(result.processed_text)
                
                # Log timing information
                if result.metadata and result.metadata.get('from_cache'):
                    logger.info("Used cached result")
                else:
                    logger.info(f"Tone change took: {result.processing_time:.2f} seconds")
            else:
                logger.error(f"Tone change failed: {result.error_message}")
                
        except Exception as e:
            logger.error(f"Error in change_tone: {e}")
    
    def exit_app(self) -> None:
        """Handle Ctrl+Shift+E - Exit application."""
        logger.info("Ctrl+Shift+E pressed - Exiting application")
        sys.exit(0)
    
    def get_handlers(self) -> Dict[str, HotkeyHandler]:
        """Get all handlers as a dictionary."""
        return {
            'grammar_fix_line': self.grammar_fix_line,
            'grammar_fix_selection': self.grammar_fix_selection,
            'summarize': self.summarize,
            'change_tone': self.change_tone,
            'exit_app': self.exit_app,
        }


# Singleton instance
_hotkey_service: HotkeyService = None


def get_hotkey_service() -> HotkeyService:
    """Get the singleton hotkey service instance."""
    global _hotkey_service
    if _hotkey_service is None:
        _hotkey_service = HotkeyService()
    return _hotkey_service
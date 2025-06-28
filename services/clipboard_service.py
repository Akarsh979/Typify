"""
Clipboard service for handling text copy/paste operations.
Encapsulates clipboard operations and keyboard interactions.
"""
import time
import logging
from typing import Optional
from pynput.keyboard import Key, Controller
import pyperclip


logger = logging.getLogger(__name__)


class ClipboardService:
    """Service for managing clipboard operations and text selection."""
    
    def __init__(self, controller: Optional[Controller] = None):
        self.controller = controller or Controller()
    
    def copy_to_clipboard(self) -> None:
        """Copy current selection to clipboard."""
        try:
            self.controller.press(Key.ctrl)
            self.controller.press('c')
            self.controller.release('c')
            self.controller.release(Key.ctrl)
            logger.debug("Text copied to clipboard")
        except Exception as e:
            logger.error(f"Error copying to clipboard: {e}")
    
    def paste_from_clipboard(self) -> None:
        """Paste text from clipboard."""
        try:
            self.controller.press(Key.ctrl)
            self.controller.press('v')
            self.controller.release('v')
            self.controller.release(Key.ctrl)
            logger.debug("Text pasted from clipboard")
        except Exception as e:
            logger.error(f"Error pasting from clipboard: {e}")
    
    def get_clipboard_text(self, wait_time: float = 0.1) -> str:
        """Get text from clipboard with optional wait time."""
        try:
            if wait_time > 0:
                time.sleep(wait_time)
            text = pyperclip.paste()
            logger.debug(f"Retrieved text from clipboard: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error getting clipboard text: {e}")
            return ""
    
    def set_clipboard_text(self, text: str) -> None:
        """Set text to clipboard."""
        try:
            pyperclip.copy(text)
            logger.debug(f"Set clipboard text: {len(text)} characters")
        except Exception as e:
            logger.error(f"Error setting clipboard text: {e}")
    
    def select_current_line(self) -> None:
        """Select the current line."""
        try:
            # Move cursor to start of line
            self.controller.press(Key.home)
            self.controller.release(Key.home)
            
            # Hold Shift and press End to select to end of line
            self.controller.press(Key.shift)
            self.controller.press(Key.end)
            self.controller.release(Key.end)
            self.controller.release(Key.shift)
            
            logger.debug("Current line selected")
        except Exception as e:
            logger.error(f"Error selecting current line: {e}")
    
    def copy_current_line(self) -> str:
        """Select and copy the current line, returning the text."""
        try:
            self.select_current_line()
            self.copy_to_clipboard()
            return self.get_clipboard_text()
        except Exception as e:
            logger.error(f"Error copying current line: {e}")
            return ""
    
    def copy_selection(self) -> str:
        """Copy the current selection and return the text."""
        try:
            self.copy_to_clipboard()
            return self.get_clipboard_text()
        except Exception as e:
            logger.error(f"Error copying selection: {e}")
            return ""
    
    def replace_selection_with_text(self, text: str) -> None:
        """Replace the current selection with new text."""
        try:
            self.set_clipboard_text(text)
            self.paste_from_clipboard()
            logger.debug("Selection replaced with new text")
        except Exception as e:
            logger.error(f"Error replacing selection: {e}")
    
    def replace_current_line_with_text(self, text: str) -> None:
        """Replace the current line with new text."""
        try:
            self.select_current_line()
            self.replace_selection_with_text(text)
            logger.debug("Current line replaced with new text")
        except Exception as e:
            logger.error(f"Error replacing current line: {e}")


# Singleton instance
_clipboard_service: Optional[ClipboardService] = None


def get_clipboard_service() -> ClipboardService:
    """Get the singleton clipboard service instance."""
    global _clipboard_service
    if _clipboard_service is None:
        _clipboard_service = ClipboardService()
    return _clipboard_service 
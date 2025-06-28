"""
Services package for Typify application.
Contains all business logic and service implementations.
"""

from .cache_service import (
    CacheService,
    LRUCache,
    CacheEntry,
    get_cache_service
)

from .clipboard_service import (
    ClipboardService,
    get_clipboard_service
)

from .hotkey_service import (
    HotkeyService,
    DefaultHotkeyHandlers,
    HotkeyHandler,
    get_hotkey_service
)

from .text_processors import (
    GrammarCorrector,
    TextSummarizer,
    ToneChanger,
    BaseTextProcessor,
    PromptTemplates
)

__all__ = [
    # Cache service
    'CacheService',
    'LRUCache', 
    'CacheEntry',
    'get_cache_service',
    
    # Clipboard service
    'ClipboardService',
    'get_clipboard_service',
    
    # Hotkey service
    'HotkeyService',
    'DefaultHotkeyHandlers',
    'HotkeyHandler',
    'get_hotkey_service',
    
    # Text processors
    'GrammarCorrector',
    'TextSummarizer',
    'ToneChanger',
    'BaseTextProcessor',
    'PromptTemplates',
] 
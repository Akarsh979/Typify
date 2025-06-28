"""
Cache service for text processing operations.
Implements caching strategies with configurable limits and cleanup.
"""
import time
import logging
from typing import Dict, Any, Optional, TypeVar, Generic
from threading import Lock
from dataclasses import dataclass, field

from config import get_config


logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class CacheEntry(Generic[T]):
    """A cache entry with metadata."""
    value: T
    created_at: float = field(default_factory=time.time)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    
    def access(self) -> T:
        """Mark the entry as accessed and return the value."""
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value


class LRUCache(Generic[T]):
    """Thread-safe LRU cache implementation."""
    
    def __init__(self, max_size: int, cleanup_batch_size: int = 20):
        self.max_size = max_size
        self.cleanup_batch_size = cleanup_batch_size
        self._cache: Dict[str, CacheEntry[T]] = {}
        self._lock = Lock()
    
    def get(self, key: str) -> Optional[T]:
        """Get a value from the cache."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                return entry.access()
            return None
    
    def put(self, key: str, value: T) -> None:
        """Put a value in the cache."""
        with self._lock:
            if len(self._cache) >= self.max_size:
                self._cleanup()
            
            self._cache[key] = CacheEntry(value)
    
    def contains(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        with self._lock:
            return key in self._cache
    
    def size(self) -> int:
        """Get the current cache size."""
        with self._lock:
            return len(self._cache)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def _cleanup(self) -> None:
        """Remove least recently used entries."""
        if len(self._cache) < self.cleanup_batch_size:
            return
        
        # Sort by last accessed time and remove oldest entries
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda item: item[1].last_accessed
        )
        
        for key, _ in sorted_entries[:self.cleanup_batch_size]:
            del self._cache[key]
        
        logger.debug(f"Cache cleanup: removed {self.cleanup_batch_size} entries")


class CacheService:
    """Service for managing multiple caches for different operations."""
    
    def __init__(self):
        self.config = get_config()
        cache_config = self.config.cache
        
        self.grammar_cache = LRUCache[str](
            max_size=cache_config.max_cache_size,
            cleanup_batch_size=cache_config.cleanup_batch_size
        )
        
        self.summary_cache = LRUCache[str](
            max_size=cache_config.max_cache_size // 2,  # Smaller cache for summaries
            cleanup_batch_size=cache_config.cleanup_batch_size
        )
        
        self.tone_cache = LRUCache[str](
            max_size=cache_config.max_cache_size // 2,  # Smaller cache for tone changes
            cleanup_batch_size=cache_config.cleanup_batch_size
        )
    
    def _normalize_key(self, text: str) -> str:
        """Normalize text for use as a cache key."""
        return text.strip().lower()
    
    def get_grammar_correction(self, text: str) -> Optional[str]:
        """Get cached grammar correction."""
        key = self._normalize_key(text)
        result = self.grammar_cache.get(key)
        if result:
            logger.debug("Using cached grammar correction")
        return result
    
    def cache_grammar_correction(self, original_text: str, corrected_text: str) -> None:
        """Cache a grammar correction."""
        key = self._normalize_key(original_text)
        self.grammar_cache.put(key, corrected_text)
    
    def get_summary(self, text: str) -> Optional[str]:
        """Get cached summary."""
        key = self._normalize_key(text)
        result = self.summary_cache.get(key)
        if result:
            logger.debug("Using cached summary")
        return result
    
    def cache_summary(self, original_text: str, summary: str) -> None:
        """Cache a summary."""
        key = self._normalize_key(original_text)
        self.summary_cache.put(key, summary)
    
    def get_tone_change(self, text: str, tone: str = "formal") -> Optional[str]:
        """Get cached tone change."""
        key = f"{self._normalize_key(text)}_{tone}"
        result = self.tone_cache.get(key)
        if result:
            logger.debug("Using cached tone change")
        return result
    
    def cache_tone_change(self, original_text: str, changed_text: str, tone: str = "formal") -> None:
        """Cache a tone change."""
        key = f"{self._normalize_key(original_text)}_{tone}"
        self.tone_cache.put(key, changed_text)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about cache usage."""
        return {
            'grammar_cache_size': self.grammar_cache.size(),
            'summary_cache_size': self.summary_cache.size(),
            'tone_cache_size': self.tone_cache.size(),
            'grammar_cache_max': self.grammar_cache.max_size,
            'summary_cache_max': self.summary_cache.max_size,
            'tone_cache_max': self.tone_cache.max_size
        }
    
    def clear_all_caches(self) -> None:
        """Clear all caches."""
        self.grammar_cache.clear()
        self.summary_cache.clear()
        self.tone_cache.clear()
        logger.info("All caches cleared")


# Singleton instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get the singleton cache service instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service 
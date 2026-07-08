"""
Cache service for enterprise competitor analysis system.

Provides file-based caching with TTL support, automatic cleanup,
and graceful error handling.
"""

import json
import time
from pathlib import Path
from typing import Optional, Any, Callable, TypeVar
from dataclasses import dataclass, asdict
from datetime import datetime
from core.exceptions import CacheException


T = TypeVar('T')


@dataclass
class CacheEntry:
    """
    Cache entry data structure.
    
    Attributes:
        key: Cache key
        data: Cached data (must be JSON-serializable)
        timestamp: Entry creation timestamp
        ttl: Time-to-live in seconds
    """
    key: str
    data: Any
    timestamp: float
    ttl: int
    
    def is_expired(self) -> bool:
        """
        Check if cache entry is expired.
        
        Returns:
            True if expired, False otherwise
        """
        current_time = time.time()
        return (current_time - self.timestamp) > self.ttl
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict) -> 'CacheEntry':
        """Create from dictionary."""
        return CacheEntry(**data)


class CacheService:
    """
    File-based cache service with TTL support.
    
    Features:
    - File-based persistent storage
    - TTL-based expiration
    - Automatic cleanup of expired entries
    - Graceful error handling
    - Get-or-compute pattern support
    """
    
    def __init__(
        self,
        cache_dir: Path,
        default_ttl: int = 3600
    ):
        """
        Initialize cache service.
        
        Args:
            cache_dir: Directory for cache storage
            default_ttl: Default TTL in seconds (default: 3600 = 1 hour)
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        try:
            cache_file = self._get_cache_file_path(key)
            
            if not cache_file.exists():
                return None
            
            # Read cache entry
            with open(cache_file, 'r', encoding='utf-8') as f:
                entry_data = json.load(f)
            
            entry = CacheEntry.from_dict(entry_data)
            
            # Check expiration
            if entry.is_expired():
                # Delete expired entry
                self._delete_cache_file(key)
                return None
            
            return entry.data
            
        except Exception as e:
            # Log warning and return None (graceful degradation)
            print(f"⚠️  Cache read error for key '{key}': {str(e)}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set cached value.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl: TTL in seconds (None for default)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                data=value,
                timestamp=time.time(),
                ttl=ttl
            )
            
            # Write to file
            cache_file = self._get_cache_file_path(key)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(entry.to_dict(), f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            # Log warning and return False (graceful degradation)
            print(f"⚠️  Cache write error for key '{key}': {str(e)}")
            return False
    
    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], T],
        ttl: Optional[int] = None
    ) -> T:
        """
        Get from cache or compute and cache if missing.
        
        Args:
            key: Cache key
            compute_fn: Function to compute value on cache miss
            ttl: TTL in seconds (None for default)
            
        Returns:
            Cached or computed value
            
        Raises:
            Exception: If compute function fails
        """
        # Try to get from cache
        cached_value = self.get(key)
        
        if cached_value is not None:
            return cached_value
        
        # Cache miss - compute value
        try:
            computed_value = compute_fn()
            
            if computed_value is None:
                print(f"⚠️  Compute function returned None for key '{key}'")
                return None
            
            # Store in cache
            self.set(key, computed_value, ttl)
            
            return computed_value
            
        except Exception as e:
            # Re-raise computation errors
            raise CacheException(
                f"Failed to compute value for cache key '{key}': {str(e)}",
                cache_key=key,
                operation="compute"
            )
    
    def clear(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            Number of entries deleted
        """
        try:
            deleted_count = 0
            
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                    deleted_count += 1
                except Exception:
                    # Skip files that can't be deleted
                    pass
            
            return deleted_count
            
        except Exception as e:
            print(f"⚠️  Cache clear error: {str(e)}")
            return 0
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            Number of entries deleted
        """
        try:
            deleted_count = 0
            
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    # Read entry
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        entry_data = json.load(f)
                    
                    entry = CacheEntry.from_dict(entry_data)
                    
                    # Delete if expired
                    if entry.is_expired():
                        cache_file.unlink()
                        deleted_count += 1
                        
                except Exception:
                    # Skip files that can't be read/deleted
                    pass
            
            return deleted_count
            
        except Exception as e:
            print(f"⚠️  Cache cleanup error: {str(e)}")
            return 0
    
    def _get_cache_file_path(self, key: str) -> Path:
        """
        Get cache file path for key.
        
        Args:
            key: Cache key
            
        Returns:
            Path to cache file
        """
        # Sanitize key for filename
        safe_key = key.replace(":", "_").replace("/", "_").replace("\\", "_")
        return self.cache_dir / f"{safe_key}.json"
    
    def _delete_cache_file(self, key: str) -> bool:
        """
        Delete cache file.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            cache_file = self._get_cache_file_path(key)
            if cache_file.exists():
                cache_file.unlink()
                return True
            return False
        except Exception:
            return False

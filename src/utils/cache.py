"""Caching utilities using diskcache."""

import hashlib
import json
from typing import Any, Optional

from diskcache import Cache

from config import settings
from src.utils.logger import logger


class CacheManager:
    """Manages caching of API/RSS responses."""
    
    def __init__(self):
        """Initialize cache manager."""
        self.cache = Cache(str(settings.cache_dir))
        self.ttl_seconds = settings.cache_ttl_hours * 3600
        logger.info(f"Cache initialized at {settings.cache_dir}")
    
    def _generate_key(self, ticker: str, timeframe: str, source: str = "news") -> str:
        """
        Generate cache key from parameters.
        
        Args:
            ticker: Stock ticker symbol
            timeframe: Timeframe string
            source: Data source identifier
            
        Returns:
            Cache key string
        """
        key_data = f"{source}:{ticker.upper()}:{timeframe}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, ticker: str, timeframe: str, source: str = "news") -> Optional[Any]:
        """
        Retrieve cached data.
        
        Args:
            ticker: Stock ticker symbol
            timeframe: Timeframe string
            source: Data source identifier
            
        Returns:
            Cached data or None if not found/expired
        """
        key = self._generate_key(ticker, timeframe, source)
        data = self.cache.get(key)
        
        if data is not None:
            logger.debug(f"Cache HIT for {ticker} ({timeframe})")
        else:
            logger.debug(f"Cache MISS for {ticker} ({timeframe})")
        
        return data
    
    def set(self, ticker: str, timeframe: str, data: Any, source: str = "news") -> None:
        """
        Store data in cache.
        
        Args:
            ticker: Stock ticker symbol
            timeframe: Timeframe string
            data: Data to cache
            source: Data source identifier
        """
        key = self._generate_key(ticker, timeframe, source)
        self.cache.set(key, data, expire=self.ttl_seconds)
        logger.debug(f"Cached data for {ticker} ({timeframe}), TTL={self.ttl_seconds}s")
    
    def clear(self) -> None:
        """Clear all cache."""
        self.cache.clear()
        logger.info("Cache cleared")


# Global cache instance
cache_manager = CacheManager()

"""Rate limiting utilities."""

import time
from functools import wraps
from typing import Callable

from src.utils.logger import logger


class RateLimiter:
    """Simple rate limiter using token bucket algorithm."""
    
    def __init__(self, max_calls: int, period_seconds: float):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed
            period_seconds: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period_seconds
        self.calls: list[float] = []
    
    def __call__(self, func: Callable) -> Callable:
        """
        Decorator to apply rate limiting to a function.
        
        Args:
            func: Function to rate limit
            
        Returns:
            Wrapped function with rate limiting
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Remove old calls outside the period
            self.calls = [call_time for call_time in self.calls if now - call_time < self.period]
            
            # Check if we've exceeded the limit
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                if sleep_time > 0:
                    logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f}s")
                    time.sleep(sleep_time)
                    # Reset after sleep
                    self.calls = []
            
            # Record this call
            self.calls.append(time.time())
            
            return func(*args, **kwargs)
        
        return wrapper


def delay(min_seconds: float, max_seconds: float) -> Callable:
    """
    Decorator to add random delay before function execution.
    
    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds
        
    Returns:
        Decorator function
    """
    import random
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay_time = random.uniform(min_seconds, max_seconds)
            logger.debug(f"Delaying {delay_time:.2f}s before {func.__name__}")
            time.sleep(delay_time)
            return func(*args, **kwargs)
        return wrapper
    return decorator

"""Configuration management for Stock Ticker News Summarizer."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # LLM Configuration
    llm_provider: Literal["ollama", "gemini"] = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    gemini_api_key: str = ""
    
    # Cache Settings
    cache_type: str = "disk"
    cache_dir: Path = Path(".cache")
    cache_ttl_hours: int = 4
    
    # Logging
    log_level: str = "INFO"
    
    # User Agent
    user_agent: str = "StockSummarizer/1.0 (Educational)"
    
    # News Source Settings
    max_articles_per_source: int = 20
    scraper_delay_min: int = 1
    scraper_delay_max: int = 3
    
    # RSS Feed URLs
    rss_feeds: dict[str, str] = {
        "marketwatch": "https://www.marketwatch.com/rss/topstories",
        "seeking_alpha": "https://seekingalpha.com/feed.xml",
        "investing": "https://www.investing.com/rss/news.rss",
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

"""Pydantic models for data validation."""

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, HttpUrl, Field


class NewsArticle(BaseModel):
    """Represents a single news article."""
    
    title: str = Field(..., description="Article title")
    source: str = Field(..., description="News source (e.g., MarketWatch)")
    published_date: datetime = Field(..., description="Publication date/time")
    url: HttpUrl = Field(..., description="Article URL")
    content: str = Field(default="", description="Article content/summary")
    ticker_mentions: list[str] = Field(default_factory=list, description="Stock tickers mentioned")
    sentiment_score: Optional[float] = Field(default=None, ge=-1.0, le=1.0, description="Sentiment score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Apple Stock Rises on Strong iPhone Sales",
                "source": "MarketWatch",
                "published_date": "2026-01-11T10:30:00Z",
                "url": "https://example.com/article",
                "content": "Apple Inc. shares rose 2% today...",
                "ticker_mentions": ["AAPL"],
                "sentiment_score": 0.7
            }
        }


class TickerQuery(BaseModel):
    """User query for stock ticker news."""
    
    ticker: str = Field(..., description="Stock ticker symbol (e.g., AAPL)")
    option: Literal[1, 2] = Field(..., description="1 for AI summary, 2 for curated news")
    timeframe: str = Field(..., description="Timeframe (e.g., 24h, 7d, 30d)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "option": 1,
                "timeframe": "7d"
            }
        }


class SummaryResult(BaseModel):
    """Result of AI summarization (Option 1)."""
    
    ticker: str
    timeframe: str
    summary: str = Field(..., description="AI-generated summary")
    key_points: list[str] = Field(default_factory=list, description="Key takeaways")
    sentiment: Optional[str] = Field(default=None, description="Overall sentiment (positive/negative/neutral)")
    sources: list[str] = Field(default_factory=list, description="Source URLs")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "timeframe": "7d",
                "summary": "Apple stock showed strong performance this week...",
                "key_points": ["iPhone sales exceeded expectations", "New product announcements"],
                "sentiment": "positive",
                "sources": ["https://example.com/article1"],
                "generated_at": "2026-01-11T15:00:00Z"
            }
        }


class CuratedResult(BaseModel):
    """Result of news curation (Option 2)."""
    
    ticker: str
    timeframe: str
    articles: list[NewsArticle] = Field(..., description="Curated articles ranked by relevance")
    total_found: int = Field(..., description="Total articles found before filtering")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "timeframe": "7d",
                "articles": [],
                "total_found": 45,
                "generated_at": "2026-01-11T15:00:00Z"
            }
        }

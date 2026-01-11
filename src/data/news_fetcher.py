"""News fetcher orchestrator combining RSS and scraping."""

from datetime import datetime, timedelta
from typing import List

from src.data.rss_client import RSSClient
from src.data.scraper import WebScraper
from src.models.article import NewsArticle
from src.utils.cache import cache_manager
from src.utils.logger import logger


class NewsFetcher:
    """Main news fetcher that combines RSS and web scraping."""
    
    def __init__(self, use_cache: bool = True):
        """
        Initialize news fetcher.
        
        Args:
            use_cache: Whether to use caching
        """
        self.rss_client = RSSClient()
        self.scraper = WebScraper()
        self.use_cache = use_cache
    
    def _parse_timeframe(self, timeframe: str) -> datetime:
        """
        Parse timeframe string into datetime cutoff.
        
        Args:
            timeframe: Timeframe string (e.g., '24h', '7d', '30d')
            
        Returns:
            Cutoff datetime
        """
        now = datetime.utcnow()
        
        if timeframe.endswith('h'):
            hours = int(timeframe[:-1])
            return now - timedelta(hours=hours)
        elif timeframe.endswith('d'):
            days = int(timeframe[:-1])
            return now - timedelta(days=days)
        else:
            # Default to 7 days
            logger.warning(f"Unknown timeframe '{timeframe}', defaulting to 7 days")
            return now - timedelta(days=7)
    
    def _filter_by_timeframe(self, articles: List[NewsArticle], timeframe: str) -> List[NewsArticle]:
        """
        Filter articles by timeframe.
        
        Args:
            articles: List of articles
            timeframe: Timeframe string
            
        Returns:
            Filtered articles
        """
        cutoff = self._parse_timeframe(timeframe)
        filtered = [a for a in articles if a.published_date >= cutoff]
        logger.info(f"Filtered {len(articles)} -> {len(filtered)} articles within {timeframe}")
        return filtered
    
    def _deduplicate(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Remove duplicate articles based on title similarity.
        
        Args:
            articles: List of articles
            
        Returns:
            Deduplicated articles
        """
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            # Normalize title for comparison
            normalized_title = article.title.lower().strip()
            
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_articles.append(article)
        
        logger.info(f"Deduplicated {len(articles)} -> {len(unique_articles)} articles")
        return unique_articles
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        Validate ticker symbol (basic validation).
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            True if valid format
        """
        if not ticker or not ticker.isalpha():
            return False
        if len(ticker) < 1 or len(ticker) > 5:
            return False
        return True
    
    def fetch_news(self, ticker: str, timeframe: str) -> List[NewsArticle]:
        """
        Fetch news articles for a ticker within a timeframe.
        
        Args:
            ticker: Stock ticker symbol
            timeframe: Timeframe string (e.g., '24h', '7d', '30d')
            
        Returns:
            List of news articles
        """
        ticker = ticker.upper()
        
        # Validate ticker
        if not self.validate_ticker(ticker):
            logger.error(f"Invalid ticker symbol: {ticker}")
            return []
        
        # Check cache first
        if self.use_cache:
            cached = cache_manager.get(ticker, timeframe)
            if cached is not None:
                logger.info(f"Using cached data for {ticker} ({timeframe})")
                return cached
        
        # Fetch from RSS feeds (primary)
        logger.info(f"Fetching news for {ticker} from RSS feeds...")
        articles = self.rss_client.fetch_all_sources(ticker)
        
        # If RSS didn't yield many results, try scraping
        if len(articles) < 5:
            logger.info(f"RSS returned few articles ({len(articles)}), trying web scraping...")
            scraped_articles = self.scraper.scrape_all_sources(ticker)
            articles.extend(scraped_articles)
        
        # Filter by timeframe
        articles = self._filter_by_timeframe(articles, timeframe)
        
        # Deduplicate
        articles = self._deduplicate(articles)
        
        # Sort by date (most recent first)
        articles.sort(key=lambda x: x.published_date, reverse=True)
        
        # Cache results
        if self.use_cache:
            cache_manager.set(ticker, timeframe, articles)
        
        logger.info(f"Final article count for {ticker}: {len(articles)}")
        return articles

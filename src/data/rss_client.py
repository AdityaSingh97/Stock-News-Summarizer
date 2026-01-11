"""RSS feed client for fetching financial news."""

from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import quote

import feedparser
import requests

from config import settings
from src.models.article import NewsArticle
from src.utils.logger import logger
from src.utils.rate_limiter import RateLimiter, delay


class RSSClient:
    """Client for fetching news from RSS feeds."""
    
    def __init__(self):
        """Initialize RSS client."""
        self.headers = {"User-Agent": settings.user_agent}
        self.rate_limiter = RateLimiter(max_calls=10, period_seconds=60)
    
    @delay(min_seconds=1, max_seconds=2)
    def _fetch_feed(self, url: str) -> Optional[feedparser.FeedParserDict]:
        """
        Fetch and parse RSS feed.
        
        Args:
            url: RSS feed URL
            
        Returns:
            Parsed feed or None if error
        """
        try:
            logger.debug(f"Fetching RSS feed: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"RSS feed has errors: {feed.bozo_exception}")
            
            return feed
        except requests.RequestException as e:
            logger.error(f"Error fetching RSS feed {url}: {e}")
            return None
    
    def fetch_from_marketwatch(self, ticker: str) -> list[NewsArticle]:
        """
        Fetch news from MarketWatch RSS.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of news articles
        """
        # MarketWatch has ticker-specific RSS feeds
        url = f"https://www.marketwatch.com/rss/topics/{ticker.lower()}"
        return self._parse_feed(url, "MarketWatch", ticker)
    
    def fetch_from_yahoo_finance(self, ticker: str) -> list[NewsArticle]:
        """
        Fetch news from Yahoo Finance RSS.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of news articles
        """
        url = f"https://finance.yahoo.com/rss/headline?s={ticker.upper()}"
        return self._parse_feed(url, "Yahoo Finance", ticker)
    
    def fetch_from_seeking_alpha(self, ticker: str) -> list[NewsArticle]:
        """
        Fetch news from Seeking Alpha RSS.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of news articles
        """
        url = f"https://seekingalpha.com/api/sa/combined/{ticker.upper()}.xml"
        return self._parse_feed(url, "Seeking Alpha", ticker)
    
    def fetch_from_generic_feed(self, url: str, source_name: str, ticker: str) -> list[NewsArticle]:
        """
        Fetch news from any RSS feed.
        
        Args:
            url: RSS feed URL
            source_name: Name of the news source
            ticker: Stock ticker to filter by
            
        Returns:
            List of news articles
        """
        return self._parse_feed(url, source_name, ticker)
    
    def _parse_feed(self, url: str, source: str, ticker: str) -> list[NewsArticle]:
        """
        Parse RSS feed into NewsArticle objects.
        
        Args:
            url: RSS feed URL
            source: Source name
            ticker: Stock ticker to check for mentions
            
        Returns:
            List of NewsArticle objects
        """
        feed = self._fetch_feed(url)
        
        if not feed or not hasattr(feed, 'entries'):
            return []
        
        articles = []
        ticker_upper = ticker.upper()
        
        for entry in feed.entries[:settings.max_articles_per_source]:
            try:
                # Parse publication date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])
                else:
                    pub_date = datetime.utcnow()
                
                # Extract content
                content = ""
                if hasattr(entry, 'summary'):
                    content = entry.summary
                elif hasattr(entry, 'description'):
                    content = entry.description
                
                # Check if ticker is mentioned in title or content
                title = entry.get('title', '')
                full_text = f"{title} {content}".upper()
                
                # Only include if ticker is mentioned
                if ticker_upper in full_text or ticker.upper() in full_text:
                    article = NewsArticle(
                        title=title,
                        source=source,
                        published_date=pub_date,
                        url=entry.get('link', ''),
                        content=content,
                        ticker_mentions=[ticker_upper]
                    )
                    articles.append(article)
                    logger.debug(f"Found article: {title[:50]}...")
            
            except Exception as e:
                logger.warning(f"Error parsing feed entry: {e}")
                continue
        
        logger.info(f"Fetched {len(articles)} articles from {source} for {ticker}")
        return articles
    
    def fetch_all_sources(self, ticker: str) -> list[NewsArticle]:
        """
        Fetch news from all available RSS sources.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Combined list of articles from all sources
        """
        all_articles = []
        
        # Try MarketWatch
        all_articles.extend(self.fetch_from_marketwatch(ticker))
        
        # Try Yahoo Finance
        all_articles.extend(self.fetch_from_yahoo_finance(ticker))
        
        # Try Seeking Alpha
        all_articles.extend(self.fetch_from_seeking_alpha(ticker))
        
        # Generic news feeds (these will need ticker filtering)
        for feed_name, feed_url in settings.rss_feeds.items():
            all_articles.extend(self.fetch_from_generic_feed(feed_url, feed_name, ticker))
        
        logger.info(f"Total articles fetched from all sources: {len(all_articles)}")
        return all_articles

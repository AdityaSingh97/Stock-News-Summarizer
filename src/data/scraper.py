"""Web scraper for fallback news fetching."""

import time
from datetime import datetime
from typing import Optional
from urllib import robotparser
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from config import settings
from src.models.article import NewsArticle
from src.utils.logger import logger
from src.utils.rate_limiter import delay


class WebScraper:
    """Ethical web scraper for financial news sites."""
    
    def __init__(self):
        """Initialize web scraper."""
        self.headers = {"User-Agent": settings.user_agent}
        self.robot_parsers: dict[str, robotparser.RobotFileParser] = {}
    
    def _can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt.
        
        Args:
            url: URL to check
            
        Returns:
            True if allowed to fetch
        """
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Get or create robot parser for this domain
        if base_url not in self.robot_parsers:
            rp = robotparser.RobotFileParser()
            rp.set_url(f"{base_url}/robots.txt")
            try:
                rp.read()
                self.robot_parsers[base_url] = rp
            except Exception as e:
                logger.warning(f"Could not read robots.txt for {base_url}: {e}")
                # If can't read robots.txt, assume allowed
                return True
        
        rp = self.robot_parsers[base_url]
        can_fetch = rp.can_fetch(settings.user_agent, url)
        
        if not can_fetch:
            logger.warning(f"robots.txt disallows fetching {url}")
        
        return can_fetch
    
    @delay(min_seconds=settings.scraper_delay_min, max_seconds=settings.scraper_delay_max)
    def _fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch page content with delays and robots.txt respect.
        
        Args:
            url: Page URL
            
        Returns:
            Page HTML or None if error
        """
        if not self._can_fetch(url):
            return None
        
        try:
            logger.debug(f"Scraping: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def scrape_yahoo_finance(self, ticker: str) -> list[NewsArticle]:
        """
        Scrape news from Yahoo Finance.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of news articles
        """
        url = f"https://finance.yahoo.com/quote/{ticker.upper()}/news"
        html = self._fetch_page(url)
        
        if not html:
            return []
        
        articles = []
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Find news items (structure may vary, this is a general approach)
            news_items = soup.find_all('h3', class_='Fw(b)')
            
            for item in news_items[:10]:  # Limit to 10 articles
                try:
                    link_tag = item.find('a')
                    if not link_tag:
                        continue
                    
                    title = link_tag.get_text(strip=True)
                    article_url = link_tag.get('href', '')
                    
                    if not article_url.startswith('http'):
                        article_url = f"https://finance.yahoo.com{article_url}"
                    
                    article = NewsArticle(
                        title=title,
                        source="Yahoo Finance",
                        published_date=datetime.utcnow(),
                        url=article_url,
                        content="",
                        ticker_mentions=[ticker.upper()]
                    )
                    articles.append(article)
                    
                except Exception as e:
                    logger.warning(f"Error parsing news item: {e}")
                    continue
            
            logger.info(f"Scraped {len(articles)} articles from Yahoo Finance")
            
        except Exception as e:
            logger.error(f"Error parsing Yahoo Finance page: {e}")
        
        return articles
    
    def scrape_marketwatch(self, ticker: str) -> list[NewsArticle]:
        """
        Scrape news from MarketWatch.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of news articles
        """
        url = f"https://www.marketwatch.com/investing/stock/{ticker.lower()}"
        html = self._fetch_page(url)
        
        if not html:
            return []
        
        articles = []
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Find news headlines
            news_items = soup.find_all('a', class_='link')
            
            for item in news_items[:10]:
                try:
                    title = item.get_text(strip=True)
                    article_url = item.get('href', '')
                    
                    if not title or len(title) < 10:
                        continue
                    
                    if not article_url.startswith('http'):
                        article_url = f"https://www.marketwatch.com{article_url}"
                    
                    article = NewsArticle(
                        title=title,
                        source="MarketWatch",
                        published_date=datetime.utcnow(),
                        url=article_url,
                        content="",
                        ticker_mentions=[ticker.upper()]
                    )
                    articles.append(article)
                    
                except Exception as e:
                    logger.warning(f"Error parsing news item: {e}")
                    continue
            
            logger.info(f"Scraped {len(articles)} articles from MarketWatch")
            
        except Exception as e:
            logger.error(f"Error parsing MarketWatch page: {e}")
        
        return articles
    
    def scrape_all_sources(self, ticker: str) -> list[NewsArticle]:
        """
        Scrape news from all available sources.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Combined list of articles
        """
        all_articles = []
        
        # Yahoo Finance
        all_articles.extend(self.scrape_yahoo_finance(ticker))
        
        # MarketWatch
        all_articles.extend(self.scrape_marketwatch(ticker))
        
        logger.info(f"Total articles scraped: {len(all_articles)}")
        return all_articles

"""News curator for Option 2."""

from typing import List

from src.curation.scorer import NewsScorer
from src.models.article import NewsArticle, CuratedResult
from src.utils.logger import logger


class NewsCurator:
    """Curates and ranks news articles."""
    
    def __init__(self):
        """Initialize curator."""
        self.scorer = NewsScorer()
    
    def _remove_duplicates(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Remove duplicate articles with more advanced detection.
        
        Args:
            articles: List of articles
            
        Returns:
            Deduplicated list
        """
        seen_urls = set()
        seen_titles = set()
        unique = []
        
        for article in articles:
            # Normalize for comparison
            url = str(article.url).lower()
            title = article.title.lower().strip()
            
            # Check if we've seen this URL or very similar title
            if url not in seen_urls and title not in seen_titles:
                seen_urls.add(url)
                seen_titles.add(title)
                unique.append(article)
        
        logger.info(f"Removed {len(articles) - len(unique)} duplicate articles")
        return unique
    
    def _filter_low_quality(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Filter out low-quality articles.
        
        Args:
            articles: List of articles
            
        Returns:
            Filtered list
        """
        filtered = []
        
        for article in articles:
            # Filter criteria
            if len(article.title) < 10:
                continue
            if not article.url:
                continue
            
            filtered.append(article)
        
        logger.info(f"Filtered out {len(articles) - len(filtered)} low-quality articles")
        return filtered
    
    def curate_news(
        self,
        articles: List[NewsArticle],
        ticker: str,
        limit: int = 10
    ) -> CuratedResult:
        """
        Curate and rank news articles.
        
        Args:
            articles: List of articles to curate
            ticker: Stock ticker symbol
            limit: Maximum number of articles to return
            
        Returns:
            Curated result with ranked articles
        """
        total_found = len(articles)
        logger.info(f"Curating {total_found} articles for {ticker}")
        
        # Remove duplicates
        articles = self._remove_duplicates(articles)
        
        # Filter low quality
        articles = self._filter_low_quality(articles)
        
        # Rank by relevance
        articles = self.scorer.rank_articles(articles, ticker)
        
        # Limit results
        articles = articles[:limit]
        
        logger.info(f"Final curated count: {len(articles)} articles")
        
        return CuratedResult(
            ticker=ticker,
            timeframe="",  # Will be set by caller
            articles=articles,
            total_found=total_found
        )

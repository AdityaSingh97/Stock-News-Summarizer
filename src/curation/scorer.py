"""News curation and relevance scoring."""

from datetime import datetime
from typing import List

from src.models.article import NewsArticle, CuratedResult
from src.utils.logger import logger


class NewsScorer:
    """Scores articles based on relevance."""
    
    # Source credibility weights
    SOURCE_WEIGHTS = {
        "MarketWatch": 1.0,
        "Yahoo Finance": 0.9,
        "Seeking Alpha": 0.95,
        "CNBC": 1.0,
        "Reuters": 1.0,
        "Bloomberg": 1.0,
        "Wall Street Journal": 1.0,
    }
    
    def calculate_relevance(self, article: NewsArticle, ticker: str) -> float:
        """
        Calculate relevance score for an article.
        
        Args:
            article: News article
            ticker: Stock ticker to score relevance for
            
        Returns:
            Relevance score (0-100)
        """
        score = 0.0
        ticker_upper = ticker.upper()
        
        # 1. Recency score (0-40 points)
        # More recent = higher score
        hours_old = (datetime.utcnow() - article.published_date).total_seconds() / 3600
        if hours_old < 24:
            recency_score = 40
        elif hours_old < 72:
            recency_score = 30
        elif hours_old < 168:  # 7 days
            recency_score = 20
        else:
            recency_score = 10
        score += recency_score
        
        # 2. Source credibility (0-20 points)
        source_weight = self.SOURCE_WEIGHTS.get(article.source, 0.7)
        score += source_weight * 20
        
        # 3. Ticker mention frequency (0-30 points)
        title_lower = article.title.lower()
        content_lower = article.content.lower()
        ticker_lower = ticker.lower()
        
        # Title mentions are more important
        title_mentions = title_lower.count(ticker_lower) + title_lower.count(ticker_upper.lower())
        content_mentions = content_lower.count(ticker_lower) + content_lower.count(ticker_upper.lower())
        
        mention_score = min(title_mentions * 15 + content_mentions * 2, 30)
        score += mention_score
        
        # 4. Content quality (0-10 points)
        # Longer, more detailed content is generally better
        content_length = len(article.content)
        if content_length > 500:
            score += 10
        elif content_length > 200:
            score += 7
        elif content_length > 100:
            score += 5
        else:
            score += 3
        
        return min(score, 100)  # Cap at 100
    
    def rank_articles(self, articles: List[NewsArticle], ticker: str) -> List[NewsArticle]:
        """
        Rank articles by relevance.
        
        Args:
            articles: List of articles
            ticker: Stock ticker
            
        Returns:
            Sorted list of articles (most relevant first)
        """
        # Calculate scores
        scored_articles = [
            (article, self.calculate_relevance(article, ticker))
            for article in articles
        ]
        
        # Sort by score descending
        scored_articles.sort(key=lambda x: x[1], reverse=True)
        
        # Log top scores
        logger.debug(f"Top 5 relevance scores: {[s for _, s in scored_articles[:5]]}")
        
        return [article for article, score in scored_articles]

"""Prompt templates for LLM summarization."""

FINANCIAL_SUMMARY_TEMPLATE = """You are a financial analyst assistant. Analyze the following news articles about {ticker} and provide a comprehensive summary.

**Articles:**
{articles_text}

**Instructions:**
1. Provide a 300-500 word summary of the key financial news and trends for {ticker} within the {timeframe} timeframe
2. Focus on material events, financial performance, market sentiment, and notable developments
3. Extract 3-5 key bullet points highlighting the most important takeaways
4. Assess the overall sentiment (positive, negative, or neutral) based on the news
5. Be factual and grounded in the provided articles - do not hallucinate information
6. If articles contain contradictory information, acknowledge it

**Format your response as JSON:**
{{
    "summary": "Your comprehensive summary here...",
    "key_points": ["Point 1", "Point 2", "Point 3"],
    "sentiment": "positive/negative/neutral",
    "confidence": "high/medium/low"
}}
"""

EXTRACT_KEY_POINTS_TEMPLATE = """Extract the most important key points from these financial news articles about {ticker}:

{articles_text}

Provide 3-5 concise bullet points that capture the essential information. Focus on:
- Major financial events or announcements
- Significant price movements or market reactions
- Strategic decisions or changes
- Analyst opinions or forecasts

Return only a JSON array of strings: ["point1", "point2", "point3"]
"""

SENTIMENT_ANALYSIS_TEMPLATE = """Analyze the overall sentiment of these news articles about {ticker}:

{articles_text}

Determine if the overall sentiment is:
- Positive (bullish, optimistic, favorable news)
- Negative (bearish, pessimistic, concerning news)
- Neutral (mixed or factual reporting)

Return only a JSON object: {{"sentiment": "positive/negative/neutral", "reasoning": "brief explanation"}}
"""


def format_articles_for_prompt(articles: list, max_articles: int = 10) -> str:
    """
    Format articles for inclusion in prompts.
    
    Args:
        articles: List of NewsArticle objects
        max_articles: Maximum number of articles to include
        
    Returns:
        Formatted string of articles
    """
    formatted = []
    
    for i, article in enumerate(articles[:max_articles], 1):
        formatted.append(f"""
Article {i}:
Title: {article.title}
Source: {article.source}
Date: {article.published_date.strftime('%Y-%m-%d')}
Content: {article.content[:500]}...
URL: {article.url}
""")
    
    return "\n---\n".join(formatted)

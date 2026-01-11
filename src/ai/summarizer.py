"""LLM integration for news summarization supporting Ollama and Gemini."""

import json
from typing import Optional

from config import settings
from src.models.article import NewsArticle, SummaryResult
from src.utils.logger import logger
from src.ai.prompt_templates import (
    FINANCIAL_SUMMARY_TEMPLATE,
    format_articles_for_prompt
)


class Summarizer:
    """AI-powered news summarizer using local or cloud LLMs."""
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize summarizer.
        
        Args:
            provider: LLM provider ('ollama' or 'gemini'), defaults to settings
        """
        self.provider = provider or settings.llm_provider
        logger.info(f"Initializing summarizer with provider: {self.provider}")
        
        if self.provider == "ollama":
            self._init_ollama()
        elif self.provider == "gemini":
            self._init_gemini()
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
    def _init_ollama(self):
        """Initialize Ollama client."""
        try:
            import ollama
            self.client = ollama.Client(host=settings.ollama_base_url)
            # Test connection
            self.client.list()
            logger.info(f"Ollama initialized with model: {settings.ollama_model}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            logger.error("Make sure Ollama is running: ollama serve")
            raise
    
    def _init_gemini(self):
        """Initialize Gemini client."""
        try:
            import google.generativeai as genai
            
            if not settings.gemini_api_key:
                raise ValueError("GEMINI_API_KEY not set in environment")
            
            genai.configure(api_key=settings.gemini_api_key)
            self.client = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            raise
    
    def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama for completion.
        
        Args:
            prompt: Prompt text
            
        Returns:
            Generated text
        """
        try:
            response = self.client.chat(
                model=settings.ollama_model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            raise
    
    def _call_gemini(self, prompt: str) -> str:
        """
        Call Gemini for completion.
        
        Args:
            prompt: Prompt text
            
        Returns:
            Generated text
        """
        try:
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call the configured LLM.
        
        Args:
            prompt: Prompt text
            
        Returns:
            Generated text
        """
        if self.provider == "ollama":
            return self._call_ollama(prompt)
        elif self.provider == "gemini":
            return self._call_gemini(prompt)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _extract_json_from_response(self, response: str) -> dict:
        """
        Extract JSON from LLM response.
        
        Args:
            response: LLM response text
            
        Returns:
            Parsed JSON dict
        """
        # Try to find JSON in the response
        start_idx = response.find('{')
        end_idx = response.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            logger.warning("No JSON found in response, using fallback")
            return {
                "summary": response,
                "key_points": [],
                "sentiment": "neutral",
                "confidence": "low"
            }
        
        json_str = response[start_idx:end_idx + 1]
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {
                "summary": response,
                "key_points": [],
                "sentiment": "neutral",
                "confidence": "low"
            }
    
    def generate_summary(
        self,
        articles: list[NewsArticle],
        ticker: str,
        timeframe: str
    ) -> SummaryResult:
        """
        Generate AI summary of news articles.
        
        Args:
            articles: List of news articles
            ticker: Stock ticker symbol
            timeframe: Timeframe string
            
        Returns:
            Summary result
        """
        if not articles:
            logger.warning(f"No articles provided for {ticker}")
            return SummaryResult(
                ticker=ticker,
                timeframe=timeframe,
                summary=f"No news articles found for {ticker} in the {timeframe} timeframe.",
                key_points=[],
                sentiment="neutral",
                sources=[]
            )
        
        # Format articles for prompt
        articles_text = format_articles_for_prompt(articles)
        
        # Build prompt
        prompt = FINANCIAL_SUMMARY_TEMPLATE.format(
            ticker=ticker,
            timeframe=timeframe,
            articles_text=articles_text
        )
        
        logger.info(f"Generating summary for {ticker} using {self.provider}...")
        
        try:
            # Call LLM
            response = self._call_llm(prompt)
            
            # Parse response
            parsed = self._extract_json_from_response(response)
            
            # Extract sources
            sources = [str(article.url) for article in articles[:10]]
            
            # Create result
            result = SummaryResult(
                ticker=ticker,
                timeframe=timeframe,
                summary=parsed.get("summary", "Summary generation failed."),
                key_points=parsed.get("key_points", []),
                sentiment=parsed.get("sentiment", "neutral"),
                sources=sources
            )
            
            logger.info(f"Summary generated successfully for {ticker}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return SummaryResult(
                ticker=ticker,
                timeframe=timeframe,
                summary=f"Error generating summary: {str(e)}",
                key_points=[],
                sentiment="neutral",
                sources=[]
            )
    
    def extract_key_points(self, articles: list[NewsArticle]) -> list[str]:
        """
        Extract key points from articles.
        
        Args:
            articles: List of news articles
            
        Returns:
            List of key points
        """
        if not articles:
            return []
        
        articles_text = format_articles_for_prompt(articles, max_articles=5)
        
        from src.ai.prompt_templates import EXTRACT_KEY_POINTS_TEMPLATE
        
        prompt = EXTRACT_KEY_POINTS_TEMPLATE.format(
            ticker=articles[0].ticker_mentions[0] if articles[0].ticker_mentions else "UNKNOWN",
            articles_text=articles_text
        )
        
        try:
            response = self._call_llm(prompt)
            # Try to parse as JSON array
            parsed = json.loads(response)
            if isinstance(parsed, list):
                return parsed
            return []
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return []

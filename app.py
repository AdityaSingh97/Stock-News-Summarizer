import streamlit as st
import os
import sys
from datetime import datetime

# Add the project directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from src.data.news_fetcher import NewsFetcher
from src.ai.summarizer import Summarizer
from src.curation.curator import NewsCurator

# Page setup
st.set_page_config(
    page_title="Stock News Summarizer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar configuration
st.sidebar.title("Configuration")

# LLM Configuration in Sidebar
st.sidebar.subheader("LLM Settings")
llm_provider = st.sidebar.selectbox(
    "LLM Provider",
    options=["Ollama (Local/Ngrok)", "Gemini"],
    index=0
)

if "Ollama" in llm_provider:
    # Allow user to override the Ollama URL for remote access
    ollama_url = st.sidebar.text_input(
        "Ollama Base URL", 
        value=settings.ollama_base_url,
        help="Use 'http://localhost:11434' for local, or your Ngrok URL for remote access"
    )
    # Update settings
    settings.llm_provider = "ollama"
    settings.ollama_base_url = ollama_url
    
    ollama_model = st.sidebar.text_input("Model Name", value=settings.ollama_model)
    settings.ollama_model = ollama_model
else:
    settings.llm_provider = "gemini"
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
    if api_key:
        settings.gemini_api_key = api_key

# Main content
st.title("📈 Stock Ticker News Summarizer")
st.markdown("Get AI-powered summaries or curated news for any stock ticker.")

# Input area
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    ticker = st.text_input("Stock Ticker", placeholder="e.g. AAPL, NVDA, TSLA").upper()

with col2:
    option = st.selectbox("Action", ["AI Summary", "Curated News"])

with col3:
    timeframe = st.selectbox("Timeframe", ["24h", "7d", "30d"], index=1)

if st.button("Analyze", type="primary"):
    if not ticker:
        st.error("Please enter a ticker symbol.")
    else:
        with st.spinner(f"Fetching news for {ticker}..."):
            try:
                # Fetch news
                fetcher = NewsFetcher()
                articles = fetcher.fetch_news(ticker, timeframe)
                
                if not articles:
                    st.warning(f"No news found for {ticker} in the last {timeframe}.")
                else:
                    st.success(f"Found {len(articles)} articles!")
                    
                    if option == "AI Summary":
                        with st.status("Generating AI Summary...", expanded=True) as status:
                            st.write("Initializing LLM...")
                            summarizer = Summarizer()
                            st.write("Analyzing articles...")
                            result = summarizer.generate_summary(articles, ticker, timeframe)
                            status.update(label="Complete!", state="complete", expanded=False)
                        
                        # Display Summary
                        st.subheader(f"🤖 AI Analysis: {ticker}")
                        
                        # Sentiment Badge
                        sentiment_color = {
                            "positive": "green",
                            "negative": "red",
                            "neutral": "gray"
                        }.get(result.sentiment, "gray")
                        
                        st.markdown(f"**Sentiment:** :{sentiment_color}[{result.sentiment.upper()}]")
                        
                        st.markdown("### Executive Summary")
                        st.write(result.summary)
                        
                        st.markdown("### Key Takeaways")
                        for point in result.key_points:
                            st.markdown(f"- {point}")
                            
                        with st.expander("View Sources"):
                            for source in result.sources:
                                st.markdown(f"- {source}")
                                
                    else:  # Curated News
                        with st.spinner("Ranking articles..."):
                            curator = NewsCurator()
                            result = curator.curate_news(articles, ticker, limit=15)
                            
                        st.subheader(f"📰 Top Articles: {ticker}")
                        
                        for article in result.articles:
                            with st.expander(f"{article.title} ({article.source})"):
                                st.markdown(f"**Published:** {article.published_date}")
                                st.markdown(f"[Read Article]({article.url})")
                                if article.content:
                                    st.caption(article.content[:200] + "...")
                                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                # Show traceback in expander for debugging
                import traceback
                with st.expander("Debug Details"):
                    st.code(traceback.format_exc())

# Footer
st.markdown("---")
st.caption("News Summarizer v1.0 | Built with Streamlit & Ollama")

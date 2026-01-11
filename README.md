# Stock Ticker News Summarizer

A free, open-source stock ticker news summarizer that aggregates financial news from multiple sources and provides AI-powered summaries or curated article lists.

## Features

- 📰 **Multi-Source News Aggregation**: Fetches from RSS feeds (MarketWatch, Yahoo Finance, Seeking Alpha, CNBC)
- 🤖 **AI Summarization**: Generate comprehensive summaries using Ollama (local) or Gemini (cloud)
- 📊 **Smart Curation**: Relevance-based ranking and filtering
- 💾 **Caching**: Intelligent caching to reduce API calls
- 🔒 **Privacy**: Run completely offline with Ollama
- 🆓 **100% Free**: No API costs with Ollama, or use Gemini's free tier

## Installation

### Prerequisites

- Python 3.10 or higher
- (Optional) Ollama for local LLM - [Download here](https://ollama.com)

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and configure your LLM choice
```

### Option A: Using Ollama (Recommended - Free & Private)

1. Install Ollama from https://ollama.com

2. Pull a model:
```bash
ollama pull llama3.2
# Or other models: mistral, gemma2, etc.
```

3. Verify Ollama is running:
```bash
ollama list
```

4. Configure `.env`:
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
```

### Option B: Using Gemini Free Tier

1. Get a free API key from https://ai.google.dev/

2. Configure `.env`:
```
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
```

## Usage

### Option 1: AI Summary

Generate an AI-powered summary of news trends:

```bash
python main.py AAPL --option 1 --timeframe 7d
```

### Option 2: Curated News List

Get a ranked list of the most relevant articles:

```bash
python main.py TSLA --option 2 --timeframe 24h
```

### Command-Line Options

```
Usage: main.py [OPTIONS] TICKER

Arguments:
  TICKER    Stock ticker symbol (e.g., AAPL, TSLA, GOOGL)

Options:
  -o, --option [1|2]        REQUIRED: 1 for AI summary, 2 for curated list
  -t, --timeframe [24h|7d|30d]  Timeframe (default: 7d)
  -v, --verbose             Enable verbose logging
  --no-cache                Bypass cache
  -f, --output PATH         Save output to file
  -l, --limit INTEGER       Number of articles for option 2 (default: 10)
  --help                    Show this message and exit
```

### Examples

```bash
# AI summary for Apple over the last 7 days
python main.py AAPL -o 1 -t 7d

# Top 15 articles for Nvidia in the last 24 hours
python main.py NVDA -o 2 -t 24h -l 15

# Save Tesla summary to a file
python main.py TSLA -o 1 --output tesla_summary.txt

# Verbose mode with cache bypass
python main.py MSFT -o 1 -v --no-cache
```

## Architecture

```
├── config.py                  # Configuration management
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
├── src/
│   ├── data/
│   │   ├── rss_client.py     # RSS feed fetcher
│   │   ├── scraper.py        # Web scraper (fallback)
│   │   └── news_fetcher.py   # Orchestrator
│   ├── ai/
│   │   ├── prompt_templates.py
│   │   └── summarizer.py     # LLM integration
│   ├── curation/
│   │   ├── scorer.py         # Relevance scoring
│   │   └── curator.py        # News curation
│   ├── models/
│   │   └── article.py        # Pydantic models
│   └── utils/
│       ├── cache.py          # Caching layer
│       ├── logger.py         # Logging
│       └── rate_limiter.py   # Rate limiting
└── tests/                    # Unit tests
```

## Ethical Considerations

This tool follows best practices for ethical web scraping:

- ✅ Respects `robots.txt` directives
- ✅ Implements rate limiting and delays
- ✅ Uses clear User-Agent identification
- ✅ Prioritizes RSS feeds over scraping
- ✅ Caches results to minimize requests

## Configuration

Edit `.env` to customize:

- **LLM Provider**: `ollama` or `gemini`
- **Cache Duration**: `CACHE_TTL_HOURS`
- **Logging**: `LOG_LEVEL` (DEBUG, INFO, WARNING, ERROR)
- **User Agent**: Customize identification string

## Troubleshooting

### "Failed to initialize Ollama"
- Make sure Ollama is installed and running: `ollama serve`
- Check that the model is pulled: `ollama pull llama3.2`

### "No news articles found"
- Try a more common ticker symbol
- Increase the timeframe (e.g., 30d instead of 24h)
- Companies with less media coverage may have fewer articles

### Rate Limiting
- The tool automatically implements delays
- Use `--no-cache` sparingly to avoid redundant requests

## Contributing

Contributions are welcome! Feel free to:
- Add new news sources
- Improve relevance scoring
- Add tests
- Enhance error handling

## License

MIT License - Free for personal and commercial use

## Acknowledgments

- Built with best practices from the 2026 web scraping and AI summarization industry standards
- Uses free and open-source dependencies only
- Inspired by the need for accessible financial news analysis tools

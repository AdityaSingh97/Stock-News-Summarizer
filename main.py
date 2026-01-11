"""CLI commands for the stock summarizer."""

from typing import Optional

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from config import settings
from src.data.news_fetcher import NewsFetcher
from src.ai.summarizer import Summarizer
from src.curation.curator import NewsCurator
from src.models.article import NewsArticle
from src.utils.logger import logger

console = Console()


def display_summary(result):
    """Display AI summary result."""
    console.print("\n")
    console.print(Panel.fit(
        f"[bold cyan]{result.ticker}[/bold cyan] - AI Summary ({result.timeframe})",
        border_style="cyan"
    ))
    
    # Summary
    console.print("\n[bold]Summary:[/bold]")
    console.print(result.summary)
    
    # Key Points
    if result.key_points:
        console.print("\n[bold]Key Takeaways:[/bold]")
        for i, point in enumerate(result.key_points, 1):
            console.print(f"  {i}. {point}")
    
    # Sentiment
    sentiment_color = {
        "positive": "green",
        "negative": "red",
        "neutral": "yellow"
    }.get(result.sentiment, "white")
    
    console.print(f"\n[bold]Overall Sentiment:[/bold] [{sentiment_color}]{result.sentiment.upper()}[/{sentiment_color}]")
    
    # Sources
    console.print(f"\n[dim]Based on {len(result.sources)} sources[/dim]")
    console.print("\n")


def display_curated_news(result):
    """Display curated news result."""
    console.print("\n")
    console.print(Panel.fit(
        f"[bold cyan]{result.ticker}[/bold cyan] - Top {len(result.articles)} Articles ({result.timeframe})",
        border_style="cyan"
    ))
    
    console.print(f"\n[dim]Found {result.total_found} articles, showing top {len(result.articles)}[/dim]\n")
    
    # Create table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Title", style="white", width=60)
    table.add_column("Source", style="cyan", width=15)
    table.add_column("Date", style="green", width=12)
    
    for i, article in enumerate(result.articles, 1):
        table.add_row(
            str(i),
            article.title[:60],
            article.source,
            article.published_date.strftime("%Y-%m-%d")
        )
    
    console.print(table)
    
    # Show URLs
    console.print("\n[bold]Article URLs:[/bold]")
    for i, article in enumerate(result.articles, 1):
        console.print(f"  {i}. {article.url}")
    
    console.print("\n")


@click.command()
@click.argument('ticker')
@click.option('--option', '-o', type=click.Choice(['1', '2']), required=True,
              help='1 for AI summary, 2 for curated news list')
@click.option('--timeframe', '-t', type=click.Choice(['24h', '7d', '30d']), default='7d',
              help='Timeframe for news (24h, 7d, or 30d)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--no-cache', is_flag=True, help='Bypass cache')
@click.option('--output', '-f', type=click.Path(), help='Save output to file')
@click.option('--limit', '-l', type=int, default=10, help='Number of articles for option 2')
def main(ticker: str, option: str, timeframe: str, verbose: bool, no_cache: bool,
         output: Optional[str], limit: int):
    """
    Stock Ticker News Summarizer
    
    Fetch and summarize financial news for stock tickers.
    
    Examples:
    
        # Get AI summary for Apple (last 7 days)
        python main.py AAPL --option 1 --timeframe 7d
        
        # Get curated news list for Tesla (last 24 hours)
        python main.py TSLA --option 2 --timeframe 24h
        
        # Save summary to file
        python main.py NVDA --option 1 --output summary.txt
    """
    # Set log level
    if verbose:
        logger.setLevel("DEBUG")
    
    console.print(f"\n[bold]Stock Ticker News Summarizer[/bold]")
    console.print(f"Ticker: [cyan]{ticker.upper()}[/cyan] | Option: [yellow]{option}[/yellow] | Timeframe: [green]{timeframe}[/green]\n")
    
    try:
        # Fetch news
        with console.status(f"[bold green]Fetching news for {ticker.upper()}..."):
            fetcher = NewsFetcher(use_cache=not no_cache)
            articles = fetcher.fetch_news(ticker, timeframe)
        
        if not articles:
            console.print(f"[red]No news articles found for {ticker.upper()} in {timeframe} timeframe.[/red]")
            return
        
        console.print(f"[green]+[/green] Fetched {len(articles)} articles\n")
        
        # Process based on option
        if option == '1':
            # AI Summary
            with console.status("[bold green]Generating AI summary..."):
                summarizer = Summarizer()
                result = summarizer.generate_summary(articles, ticker.upper(), timeframe)
            
            display_summary(result)
            
            # Save to file if requested
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(f"{ticker.upper()} - AI Summary ({timeframe})\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"Summary:\n{result.summary}\n\n")
                    f.write(f"Key Takeaways:\n")
                    for i, point in enumerate(result.key_points, 1):
                        f.write(f"{i}. {point}\n")
                    f.write(f"\nSentiment: {result.sentiment}\n")
                    f.write(f"\nSources: {len(result.sources)}\n")
                console.print(f"[green]+[/green] Saved to {output}")
        
        else:
            # Curated News
            with console.status("[bold green]Curating top articles..."):
                curator = NewsCurator()
                result = curator.curate_news(articles, ticker.upper(), limit=limit)
                result.timeframe = timeframe
            
            display_curated_news(result)
            
            # Save to file if requested
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(f"{ticker.upper()} - Top {len(result.articles)} Articles ({timeframe})\n")
                    f.write("=" * 60 + "\n\n")
                    for i, article in enumerate(result.articles, 1):
                        f.write(f"{i}. {article.title}\n")
                        f.write(f"   Source: {article.source}\n")
                        f.write(f"   Date: {article.published_date.strftime('%Y-%m-%d')}\n")
                        f.write(f"   URL: {article.url}\n\n")
                console.print(f"[green]+[/green] Saved to {output}")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise click.Abort()


if __name__ == '__main__':
    main()


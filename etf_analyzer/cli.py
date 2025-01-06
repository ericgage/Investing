import click
from .analyzer import ETFAnalyzer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()

@click.group()
def cli():
    """ETF Analyzer - A tool for analyzing ETF performance and metrics"""
    pass

@cli.command()
@click.argument('ticker')
@click.option('--benchmark', '-b', default='SPY', help='Benchmark ETF ticker (default: SPY)')
def analyze(ticker, benchmark):
    """Analyze an ETF and display key metrics"""
    with console.status(f"[bold green]Analyzing {ticker}..."):
        analyzer = ETFAnalyzer(ticker, benchmark)
        analyzer.collect_basic_info()
        analyzer.collect_performance()
        analyzer.calculate_metrics()

    # Create summary table
    table = Table(title=f"ETF Analysis: {ticker}")
    
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    # Basic info
    table.add_row("Name", analyzer.data['basic'].get('longName', 'N/A'))
    table.add_row("Category", analyzer.data['basic'].get('category', 'N/A'))
    table.add_row("Expense Ratio", f"{analyzer.data['basic'].get('expenseRatio', 0):.2%}")
    
    # Metrics
    table.add_row("Volatility (Annualized)", f"{analyzer.metrics['volatility']:.2%}")
    table.add_row("Tracking Error", f"{analyzer.metrics['tracking_error']:.2%}")
    table.add_row("Liquidity Score", f"{analyzer.metrics['liquidity_score']:.1f}/100")
    
    console.print(table)

@cli.command()
@click.argument('tickers', nargs=-1)
def compare(tickers):
    """Compare multiple ETFs"""
    if len(tickers) < 2:
        console.print("[red]Please provide at least two tickers to compare[/red]")
        return

    table = Table(title="ETF Comparison")
    table.add_column("Metric", style="cyan")
    
    analyzers = {}
    
    with console.status("[bold green]Analyzing ETFs..."):
        for ticker in tickers:
            table.add_column(ticker.upper(), style="magenta")
            analyzer = ETFAnalyzer(ticker)
            analyzer.collect_basic_info()
            analyzer.collect_performance()
            analyzer.calculate_metrics()
            analyzers[ticker] = analyzer
    
    # Add rows for each metric
    metrics = [
        ("Expense Ratio", lambda a: f"{a.data['basic'].get('expenseRatio', 0):.2%}"),
        ("Volatility", lambda a: f"{a.metrics['volatility']:.2%}"),
        ("Tracking Error", lambda a: f"{a.metrics['tracking_error']:.2%}"),
        ("Liquidity Score", lambda a: f"{a.metrics['liquidity_score']:.1f}/100"),
    ]
    
    for metric_name, metric_func in metrics:
        row = [metric_name]
        for ticker in tickers:
            row.append(metric_func(analyzers[ticker]))
        table.add_row(*row)
    
    console.print(table)

if __name__ == '__main__':
    cli() 
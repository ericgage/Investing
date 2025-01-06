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
@click.option('--verbose', '-v', is_flag=True, help='Show detailed metrics')
@click.option('--validate', '-val', is_flag=True, help='Compare with external sources')
@click.option('--sources', '-s', is_flag=True, help='Compare different data sources')
@click.option('--history', '-h', is_flag=True, help='Show historical metrics')
def analyze(ticker, verbose, validate, sources, history):
    """Analyze an ETF with validation options"""
    try:
        with console.status(f"[bold green]Analyzing {ticker}..."):
            analyzer = ETFAnalyzer(ticker)
            analyzer.collect_basic_info()
            analyzer.collect_performance()
            analyzer.calculate_metrics()
            
            if validate:
                validation_data = analyzer.validate_metrics()

        if verbose:
            # Add detailed liquidity score breakdown
            volume_score = min(40, (analyzer.data['price_history']['Volume'].mean() / 1000000) * 4)
            spread_data = analyzer.data['price_history']
            spread_pct = ((spread_data['High'] - spread_data['Low']) / spread_data['Close']).mean() * 100
            spread_score = max(0, 30 - spread_pct * 10)
            
            console.print(f"\n[cyan]Detailed Liquidity Analysis for {ticker}:[/cyan]")
            console.print(f"Volume Score: {volume_score:.1f}/40")
            console.print(f"Spread Score: {spread_score:.1f}/30")
            console.print(f"Asset Score: {analyzer.metrics['liquidity_score'] - volume_score - spread_score:.1f}/30")

        # Create summary table
        table = Table(title=f"ETF Analysis: {ticker}")
        
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        # Basic info
        table.add_row("Name", analyzer.data['basic']['name'])
        table.add_row("Category", analyzer.data['basic']['category'])
        table.add_row("Expense Ratio", f"{analyzer.data['basic']['expenseRatio']:.2%}")
        
        # Metrics
        table.add_row("Volatility (Annualized)", f"{analyzer.metrics['volatility']:.2%}")
        table.add_row("Tracking Error", f"{analyzer.metrics['tracking_error']:.2%}")
        table.add_row("Liquidity Score", f"{analyzer.metrics['liquidity_score']:.1f}/100")
        table.add_row("Sharpe Ratio", f"{analyzer.metrics['sharpe_ratio']:.2f}")
        table.add_row("Max Drawdown", f"{analyzer.metrics['max_drawdown']:.2%}")
        
        console.print(table)
        
        if validate:
            # Validation table
            val_table = Table(title=f"Validation Results: {ticker}")
            val_table.add_column("Metric", style="cyan")
            val_table.add_column("Our Value", style="magenta")
            val_table.add_column("External Value", style="green")
            val_table.add_column("Difference", style="yellow")
            
            for metric, values in validation_data.items():
                val_table.add_row(
                    metric,
                    f"{values['our_value']:.2%}",
                    f"{values['external_value']:.2%}",
                    f"{values['difference']:.2%}"
                )
            
            console.print("\n")
            console.print(val_table)

        if sources:
            source_data = analyzer.compare_data_sources()
            # Display source comparison table
            
        if history:
            historical_data = analyzer.track_historical_metrics()
            
            # Create historical metrics table
            hist_table = Table(title=f"Historical Metrics: {ticker}")
            hist_table.add_column("Period", style="cyan")
            hist_table.add_column("Volatility", style="magenta")
            hist_table.add_column("Sharpe Ratio", style="green")
            hist_table.add_column("Max Drawdown", style="red")
            
            for period, metrics in historical_data.items():
                hist_table.add_row(
                    period,
                    f"{metrics['volatility']:.2%}",
                    f"{metrics['sharpe']:.2f}",
                    f"{metrics['max_drawdown']:.2%}"
                )
            
            console.print("\n")
            console.print(hist_table)
    except Exception as e:
        console.print(f"[red]Error analyzing {ticker}: {str(e)}[/red]")

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
        ("Sharpe Ratio", lambda a: f"{a.metrics['sharpe_ratio']:.2f}"),
        ("Max Drawdown", lambda a: f"{a.metrics['max_drawdown']:.2%}"),
    ]
    
    for metric_name, metric_func in metrics:
        row = [metric_name]
        for ticker in tickers:
            row.append(metric_func(analyzers[ticker]))
        table.add_row(*row)
    
    console.print(table)

if __name__ == '__main__':
    cli() 
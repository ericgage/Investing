import click
from .analyzer import ETFAnalyzer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()

@click.group()
def cli():
    """ETF Analysis Tool"""
    pass

@cli.command()
@click.argument('ticker')
@click.option('--benchmark', default='SPY', help='Benchmark ETF ticker')
def analyze(ticker, benchmark):
    """Analyze an ETF"""
    try:
        analyzer = ETFAnalyzer(ticker, benchmark)
        
        # Add header to output first, before any potential errors
        click.echo(f"\nETF Analysis: {ticker}")
        if benchmark != 'SPY':
            click.echo(f"Using {benchmark} as benchmark")
            
        try:
            # Collect basic info
            analyzer.collect_basic_info()
            
            # Show basic info
            click.echo("\nBasic Information:")
            click.echo(f"Name: {analyzer.data['basic']['name']}")
            click.echo(f"Category: {analyzer.data['basic']['category']}")
            click.echo(f"Expense Ratio: {analyzer.data['basic']['expenseRatio']:.3%}")
            
            # Rest of the analysis...
            
        except Exception as e:
            click.echo(f"Error collecting data: {str(e)}")
            return
            
    except Exception as e:
        click.echo(f"Error initializing analyzer: {str(e)}")
        return

@cli.command()
@click.argument('tickers', nargs=-1)
@click.option('--costs', '-c', is_flag=True, help='Include trading cost comparison')
def compare(tickers, costs):
    """Compare multiple ETFs including trading costs"""
    if len(tickers) < 2:
        console.print("[red]Please provide at least two tickers to compare[/red]")
        return

    table = Table(title="ETF Comparison")
    table.add_column("Metric", style="cyan")
    
    analyzers = {}
    cost_data = {}
    
    with console.status("[bold green]Analyzing ETFs..."):
        for ticker in tickers:
            table.add_column(ticker.upper(), style="magenta")
            analyzer = ETFAnalyzer(ticker)
            analyzer.collect_basic_info()
            analyzer.collect_performance()
            analyzer.calculate_metrics()
            analyzers[ticker] = analyzer
            
            if costs:
                cost_data[ticker] = analyzer.analyze_trading_costs()
    
    # Add rows for basic metrics
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
    
    # Add trading cost comparison if requested
    if costs and cost_data:
        cost_table = Table(title="Trading Cost Comparison")
        cost_table.add_column("Cost Component", style="cyan")
        
        for ticker in tickers:
            cost_table.add_column(ticker.upper(), style="magenta")
        
        # Add rows for each cost component
        cost_components = [
            ("Spread Cost (One-Way)", lambda d: f"{d['implicit']['spread_cost']:.3%}" if d['implicit']['spread_cost'] else "N/A"),
            ("Market Impact", lambda d: f"{d['implicit']['market_impact']:.3%}"),
            ("Total One-Way", lambda d: f"{d['total']['one_way']:.3%}"),
            ("Round-Trip", lambda d: f"{d['total']['round_trip']:.3%}"),
        ]
        
        for component_name, component_func in cost_components:
            row = [component_name]
            for ticker in tickers:
                if ticker in cost_data and cost_data[ticker]:
                    row.append(component_func(cost_data[ticker]))
                else:
                    row.append("N/A")
            cost_table.add_row(*row)
        
        console.print("\n")
        console.print(cost_table)
        
        # Show cost alerts for each ETF
        console.print("\n[yellow]Trading Cost Alerts:[/yellow]")
        for ticker in tickers:
            if ticker in cost_data and cost_data[ticker] and cost_data[ticker]['alerts']:
                console.print(f"\n[cyan]{ticker}:[/cyan]")
                for alert in cost_data[ticker]['alerts']:
                    console.print(f"[yellow]• {alert}[/yellow]")

def _get_difference_style(diff, metric):
    """Get color style based on difference magnitude and metric type"""
    if diff is None:
        return "white"
    
    # Different thresholds for different metrics
    thresholds = {
        'Expense Ratio': {'low': 0.0001, 'medium': 0.0005},  # 0.01% and 0.05%
        'AUM': {'low': 0.10, 'medium': 0.25},                # 10% and 25%
        'Volume': {'low': 0.15, 'medium': 0.30},             # 15% and 30%
    }
    
    # Get appropriate thresholds
    t = thresholds.get(metric, {'low': 0.05, 'medium': 0.15})
    
    if diff <= t['low']:
        return "green"
    elif diff <= t['medium']:
        return "yellow"
    else:
        return "red"

def _get_difference_note(diff, metric):
    """Get explanatory note for significant differences"""
    if diff is None:
        return ""
        
    notes = {
        'Expense Ratio': {
            'high': "Significant variation in expense ratio reporting",
            'medium': "Minor discrepancy in expense ratio",
            'low': ""
        },
        'AUM': {
            'high': "Large AUM difference, possibly due to reporting date mismatch",
            'medium': "AUM varies between sources",
            'low': ""
        },
        'Volume': {
            'high': "Volume differs significantly, check market conditions",
            'medium': "Volume varies between sources",
            'low': ""
        }
    }
    
    # Get appropriate thresholds and notes
    if metric in notes:
        if diff > 0.25:
            return notes[metric]['high']
        elif diff > 0.10:
            return notes[metric]['medium']
    
    return ""

if __name__ == '__main__':
    cli() 
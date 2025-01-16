import click
from .analyzer import ETFAnalyzer
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from . import __version__

console = Console()

@click.group()
@click.version_option(version=__version__)
def cli():
    """ETF Analyzer - A tool for analyzing ETF performance and metrics"""
    pass

@cli.command()
@click.argument('ticker')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed metrics')
@click.option('--validate', '-val', is_flag=True, help='Compare with external sources')
@click.option('--sources', '-s', is_flag=True, help='Compare different data sources')
@click.option('--history', '-h', is_flag=True, help='Show historical metrics')
@click.option('--costs', '-c', is_flag=True, help='Show trading cost analysis')
@click.option('--debug', '-d', is_flag=True, help='Enable debug output')
def analyze(ticker, verbose, validate, sources, history, costs, debug):
    """Analyze an ETF with validation options"""
    try:
        with console.status(f"[bold green]Analyzing {ticker}..."):
            analyzer = ETFAnalyzer(ticker, debug=debug)
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
            val_table.add_column("Difference", justify="right")
            val_table.add_column("Note", style="italic")
            
            for metric, values in validation_data.items():
                our_value = values.get('our_value')
                ext_value = values.get('external_value')
                diff = values.get('difference')
                
                # Format based on metric type
                if metric == 'AUM':
                    formatted_row = [
                        metric,
                        f"${our_value:,.0f}" if our_value is not None else "N/A",
                        f"${ext_value:,.0f}" if ext_value is not None else "N/A",
                        f"[{_get_difference_style(diff, metric)}]{diff:.1%}[/]" if diff is not None else "N/A",
                        _get_difference_note(diff, metric)
                    ]
                elif metric == 'Volume':
                    formatted_row = [
                        metric,
                        f"{our_value:,.0f}" if our_value is not None else "N/A",
                        f"{ext_value:,.0f}" if ext_value is not None else "N/A",
                        f"[{_get_difference_style(diff, metric)}]{diff:.1%}[/]" if diff is not None else "N/A",
                        _get_difference_note(diff, metric)
                    ]
                else:  # Percentage metrics like Expense Ratio
                    formatted_row = [
                        metric,
                        f"{our_value:.2%}" if our_value is not None else "N/A",
                        f"{ext_value:.2%}" if ext_value is not None else "N/A",
                        f"[{_get_difference_style(diff, metric)}]{diff:.2%}[/]" if diff is not None else "N/A",
                        _get_difference_note(diff, metric)
                    ]
                
                val_table.add_row(*formatted_row)
            
            console.print("\n")
            console.print(val_table)

        if sources:
            source_data = analyzer.compare_data_sources()
            
            # Create source comparison table
            source_table = Table(title=f"Data Source Comparison: {ticker}")
            source_table.add_column("Metric", style="cyan")
            
            # Add a column for each source
            for source in source_data.keys():
                source_table.add_column(source.capitalize(), style="magenta")
            
            # Add rows for each metric
            metrics = ['expense_ratio', 'volatility', 'volume']
            for metric in metrics:
                row = [metric.replace('_', ' ').title()]
                for source, data in source_data.items():
                    if data and metric in data:
                        value = data[metric]
                        # Format based on metric type
                        if 'ratio' in metric:
                            row.append(f"{value:.2%}")
                        elif metric == 'volume':
                            row.append(f"{value:,.0f}")
                        else:
                            row.append(f"{value:.2%}")
                    else:
                        row.append("N/A")
                source_table.add_row(*row)
            
            console.print("\n")
            console.print(source_table)

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

        if costs:
            cost_analysis = analyzer.analyze_trading_costs()
            if cost_analysis:
                console.print("\n[cyan]Trading Cost Analysis[/cyan]")
                for component, value in cost_analysis.items():
                    console.print(f"{component}: {value:.4%}")
    except Exception as e:
        console.print(f"[red]Error analyzing {ticker}: {str(e)}[/red]")

@cli.command()
@click.argument('tickers', nargs=-1)
@click.option('--costs', '-c', is_flag=True, help='Show trading cost analysis')
@click.option('--debug', '-d', is_flag=True, help='Enable debug output')
def compare(tickers, costs, debug):
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

    if costs:
        # Add cost comparison table
        cost_table = Table(title="Trading Cost Comparison")
        cost_table.add_column("Cost Component", style="cyan")
        for ticker in tickers:
            cost_table.add_column(ticker.upper(), style="magenta")
            
        cost_components = ["Expense Ratio", "Bid-Ask Spread", "Market Impact", "Total Cost"]
        for component in cost_components:
            row = [component]
            for ticker in tickers:
                costs = analyzers[ticker].analyze_trading_costs()
                row.append(f"{costs[component]:.4%}" if costs else "N/A")
            cost_table.add_row(*row)
            
        console.print("\n")
        console.print(cost_table)

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
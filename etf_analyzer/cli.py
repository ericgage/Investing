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
@click.option('--benchmark', help='Benchmark ETF ticker (default: SPY)')
@click.option('--verbose', is_flag=True, help='Show detailed analysis')
@click.option('--validate', is_flag=True, help='Compare with external data')
@click.option('--history', is_flag=True, help='Show historical metrics')
@click.option('--costs', is_flag=True, help='Show trading cost analysis')
def analyze(ticker, benchmark=None, verbose=False, validate=False, history=False, costs=False):
    """Analyze an ETF"""
    try:
        # Get benchmark and show message if explicitly provided
        was_benchmark_provided = benchmark is not None
        benchmark = benchmark or 'SPY'
        analyzer = ETFAnalyzer(ticker, benchmark)
        
        # Create main table with subtitle for benchmark
        title = f"ETF Analysis: {ticker}"
        # Show benchmark message if it was explicitly provided via command line
        if was_benchmark_provided:
            title += f"\nUsing {benchmark} as benchmark"
        
        # Create table with columns
        table = Table(title=title, show_header=True)
        table.add_column("Metric", style="cyan", justify="right")
        table.add_column("Value", style="magenta")
        
        # Add section header
        table.add_row("Basic Information", "", style="bold")
        
        # Collect and display data
        analyzer.collect_basic_info()
        analyzer.collect_performance()
        analyzer.calculate_metrics()
        
        # Basic metrics
        table.add_row("Name", analyzer.data['basic']['name'])
        table.add_row("Category", analyzer.data['basic']['category'])
        table.add_row("Expense Ratio", f"{analyzer.data['basic']['expenseRatio']:.3%}")
        table.add_row("AUM", f"${analyzer.data['basic']['totalAssets']:,.0f}")
        table.add_row("Avg Daily Volume", f"{analyzer.data['price_history']['Volume'].mean():,.0f}")
        
        # Add performance section
        table.add_row("Performance Metrics", "", style="bold")
        table.add_row("Volatility (Annualized)", f"{analyzer.metrics['volatility']:.2%}")
        table.add_row("Tracking Error", f"{analyzer.metrics['tracking_error']:.2%}")
        table.add_row("Liquidity Score", f"{analyzer.metrics['liquidity_score']:.1f}/100")
        table.add_row("Sharpe Ratio", f"{analyzer.metrics['sharpe_ratio']:.2f}")
        table.add_row("Max Drawdown", f"{analyzer.metrics['max_drawdown']:.2%}")
        
        console.print(table)
        
        # Show validation if requested
        if validate:
            validation_table = Table(title="Validation Results", show_header=True)
            validation_table.add_column("Metric", style="cyan", justify="right")
            validation_table.add_column("Our Value", style="magenta")
            validation_table.add_column("External Value", style="green")
            validation_table.add_column("Difference", style="yellow")
            
            # Get validation data
            validation_data = analyzer.validate_metrics()
            
            # Add rows for each metric
            for metric, values in validation_data.items():
                our_val = values.get('our_value')
                ext_val = values.get('external_value')
                diff = values.get('difference')
                
                # Format values based on metric type
                if metric == 'Expense Ratio':
                    our_str = f"{our_val:.3%}" if our_val is not None else "N/A"
                    ext_str = f"{ext_val:.3%}" if ext_val is not None else "N/A"
                    diff_str = f"{diff:.3%}" if diff is not None else "N/A"
                elif metric == 'AUM':
                    our_str = f"${our_val:,.0f}" if our_val is not None else "N/A"
                    ext_str = f"${ext_val:,.0f}" if ext_val is not None else "N/A"
                    diff_str = f"{diff:.1%}" if diff is not None else "N/A"
                else:  # Volume
                    our_str = f"{our_val:,.0f}" if our_val is not None else "N/A"
                    ext_str = f"{ext_val:,.0f}" if ext_val is not None else "N/A"
                    diff_str = f"{diff:.1%}" if diff is not None else "N/A"
                    
                # Get color based on difference magnitude
                diff_style = _get_difference_style(diff, metric)
                
                # Add row with explicit color style
                validation_table.add_row(
                    metric, 
                    our_str, 
                    ext_str, 
                    f"[{diff_style}]{diff_str}[/{diff_style}]"
                )
                
                # Add note if significant with severity icon
                note = _get_difference_note(diff, metric)
                if note:
                    icon = "⚠️ " if diff_style == "red" else "ℹ️ "
                    prefix = "Warning:" if diff_style == "red" else "Note:"
                    validation_table.add_row(
                        "", "", "", 
                        f"[{diff_style} dim]{icon}{prefix} {note}[/{diff_style} dim]"
                    )
            
            console.print("\n", validation_table)
        
        # Show historical metrics if requested
        if history:
            history_table = Table(title="Historical Metrics", show_header=True)
            history_table.add_column("Period", style="cyan", justify="right")
            history_table.add_column("Volatility", style="magenta")
            history_table.add_column("Sharpe Ratio", style="magenta")
            history_table.add_column("Max Drawdown", style="magenta")
            
            # Get historical data
            historical_data = analyzer.track_historical_metrics()
            
            # Add rows for each period
            for period in ['1mo', '3mo', '6mo', '1y']:
                if period in historical_data:
                    metrics = historical_data[period]
                    history_table.add_row(
                        period,
                        f"{metrics['volatility']:.2%}",
                        f"{metrics['sharpe']:.2f}",
                        f"{metrics['max_drawdown']:.2%}"
                    )
            
            console.print("\n", history_table)
            
        if verbose:
            # Add detailed liquidity analysis
            liquidity_table = Table(title=f"Detailed Liquidity Analysis for {ticker}:")
            liquidity_table.add_column("Component", style="cyan", justify="right")
            liquidity_table.add_column("Score", style="magenta")
            
            # Add rows with error handling
            liquidity_table.add_row("Volume Score", f"{analyzer.metrics.get('volume_score', 0):.1f}/40")
            liquidity_table.add_row("Spread Score", f"{analyzer.metrics.get('spread_score', 0):.1f}/30")
            liquidity_table.add_row("Asset Score", f"{analyzer.metrics.get('asset_score', 0):.1f}/30")
            liquidity_table.add_row("Total Score", f"{analyzer.metrics.get('liquidity_score', 0):.1f}/100")
            
            console.print("\n", liquidity_table)
            
        # Add trading costs section if requested
        if costs:
            cost_table = Table(
                title="Trading Cost Analysis",
                show_header=True,
                title_style="bold cyan",
                width=50
            )
            cost_table.add_column("Cost Component", style="cyan", justify="right")
            cost_table.add_column("Value", style="magenta", justify="right")
            
            costs = analyzer.analyze_trading_costs()
            expense_ratio = costs['explicit']['expense_ratio']
            
            if costs['implicit']['spread_cost'] is None:
                # No real-time data - show simplified table
                cost_table.add_row("Expense Ratio", f"{expense_ratio:.3%}")
                cost_table.add_row(
                    "Total One-Way", 
                    f"[yellow]{expense_ratio:.3%} (Exp)[/yellow]"
                )
                cost_table.add_row(
                    "Round-Trip", 
                    f"[yellow]{expense_ratio * 2:.3%} (Exp)[/yellow]"
                )
                cost_table.caption = "[dim]Note: Real-time trading costs unavailable. Showing expense ratio only.[/dim]"
            else:
                # Show full cost breakdown
                spread_cost = costs['implicit']['spread_cost']
                market_impact = costs['implicit']['market_impact']
                total = costs['total']['one_way']
                
                # Calculate percentages of total
                spread_pct = (spread_cost / total) * 100 if total > 0 else 0
                impact_pct = (market_impact / total) * 100 if total > 0 else 0
                exp_pct = (expense_ratio / total) * 100 if total > 0 else 0
                
                # Add header row to explain the format
                cost_table.add_row(
                    "[dim italic]Component[/dim italic]",
                    "[dim italic]Cost (% of Total)[/dim italic]"
                )
                
                cost_table.add_row(
                    "Spread Cost (One-Way)", 
                    f"{spread_cost:.3%} [dim]({spread_pct:.0f}% of costs)[/dim]"
                )
                cost_table.add_row(
                    "Market Impact", 
                    f"{market_impact:.3%} [dim]({impact_pct:.0f}% of costs)[/dim]"
                )
                cost_table.add_row(
                    "Expense Ratio", 
                    f"{expense_ratio:.3%} [dim]({exp_pct:.0f}% of costs)[/dim]"
                )
                
                # Add divider before totals
                cost_table.add_row("", "")  # Empty row for spacing
                cost_table.add_row("[dim]───────────[/dim]", "[dim]───────────[/dim]")
                
                cost_table.add_row("Total One-Way", f"[bold]{costs['total']['one_way']:.3%}[/bold]")
                cost_table.add_row("Round-Trip", f"[bold]{costs['total']['round_trip']:.3%}[/bold]")
            
            console.print("\n")
            console.print(cost_table)
            
            # Show alerts if any
            if costs['alerts']:
                console.print("\nTrading Cost Alerts:")
                for alert in costs['alerts']:
                    console.print(f"[yellow]• {alert}[/yellow]")

        # ... rest of the function ...

    except Exception as e:
        console.print(f"[red]Error analyzing {ticker}: {str(e)}[/red]")

@cli.command()
@click.argument('tickers', nargs=-1)
@click.option('--costs', '-c', is_flag=True, help='Include trading cost comparison')
@click.option('--debug', is_flag=True, help='Show debug messages')
def compare(tickers, costs, debug=False):
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
            try:
                analyzer = ETFAnalyzer(ticker, debug=debug)
                analyzer.collect_basic_info()
                analyzer.collect_performance()
                analyzer.calculate_metrics()
                analyzers[ticker] = analyzer
                
                if costs:
                    try:
                        analyzer.collect_real_time_data()
                        cost_data[ticker] = analyzer.analyze_trading_costs()
                        if debug:
                            # Add debug output to see the cost data structure
                            console.print(f"\nDebug: Cost data for {ticker}:")
                            console.print(cost_data[ticker])
                    except Exception as e:
                        if debug:
                            console.print(f"[yellow]Warning: Could not get trading costs for {ticker}: {str(e)}[/yellow]")
                        cost_data[ticker] = {
                            'implicit': {'spread_cost': None, 'market_impact': None},
                            'total': {'one_way': None, 'round_trip': None}
                        }
            except Exception as e:
                if debug:
                    console.print(f"[red]Error analyzing {ticker}: {str(e)}[/red]")
                analyzers[ticker] = None
    
    # Add rows for basic metrics with error handling
    metrics = [
        ("Expense Ratio", lambda a: f"{a.data['basic'].get('expenseRatio') or 0:.2%}"),
        ("Volatility", lambda a: f"{a.metrics.get('volatility', 0):.2%}"),
        ("Tracking Error", lambda a: f"{a.metrics.get('tracking_error', 0):.2%}"),
        ("Liquidity Score", lambda a: f"{a.metrics.get('liquidity_score', 0):.1f}/100"),
        ("Sharpe Ratio", lambda a: f"{a.metrics.get('sharpe_ratio', 0):.2f}"),
        ("Max Drawdown", lambda a: f"{a.metrics.get('max_drawdown', 0):.2%}"),
    ]
    
    for metric_name, metric_func in metrics:
        row = [metric_name]
        for ticker in tickers:
            try:
                if analyzers[ticker]:
                    row.append(metric_func(analyzers[ticker]))
                else:
                    row.append("N/A")
            except Exception:
                row.append("N/A")
        table.add_row(*row)
    
    console.print(table)
    
    # Add trading cost comparison if requested
    if costs:
        cost_table = Table(title="Trading Cost Analysis")
        cost_table.add_column("Cost Component", style="cyan")
        
        for ticker in tickers:
            cost_table.add_column(ticker.upper(), style="magenta")
        
        # Add rows for each cost component with safer data access
        cost_components = [
            ("Spread Cost (One-Way)", lambda d: f"{d.get('implicit', {}).get('spread_cost'):.3%}" 
                if d.get('implicit', {}).get('spread_cost') is not None else "N/A"),
            ("Market Impact", lambda d: f"{d.get('implicit', {}).get('market_impact'):.3%}"
                if d.get('implicit', {}).get('market_impact') is not None else "N/A"),
            ("Total One-Way", lambda d: f"{d.get('explicit', {}).get('expense_ratio'):.3%} (Exp)" 
                if all(d.get('implicit', {}).get(x) is None for x in ['spread_cost', 'market_impact'])
                else f"{d.get('total', {}).get('one_way'):.3%}"),
            ("Round-Trip", lambda d: f"{(d.get('explicit', {}).get('expense_ratio') * 2):.3%} (Exp)"
                if all(d.get('implicit', {}).get(x) is None for x in ['spread_cost', 'market_impact'])
                else f"{d.get('total', {}).get('round_trip'):.3%}"),
        ]
        
        # Add note about data availability
        if all(cost_data[ticker].get('implicit', {}).get('spread_cost') is None 
               for ticker in tickers if ticker in cost_data):
            cost_table.caption = "Note: Real-time trading costs unavailable. Showing expense ratios only."
        
        for component_name, component_func in cost_components:
            row = [component_name]
            for ticker in tickers:
                try:
                    if cost_data.get(ticker):
                        value = component_func(cost_data[ticker])
                        # Don't show 0.000% for missing data
                        if value == "0.000%":
                            value = "N/A"
                    else:
                        value = "N/A"
                    row.append(value)
                except Exception:
                    row.append("N/A")
            cost_table.add_row(*row)
        
        # Add market status indicator if any ETF has it
        market_status = None
        for ticker in tickers:
            if cost_data.get(ticker, {}).get('real_time', {}).get('market_status'):
                market_status = cost_data[ticker]['real_time']['market_status']
                break
                
        if market_status == 'closed':
            cost_table.title = "Trading Cost Analysis (Market Closed)"
            cost_table.caption = "Note: Using last known values where available"
        
        console.print("\n")
        console.print(cost_table)
        
        # Show cost alerts for each ETF
        alerts_found = False
        for ticker in tickers:
            if (ticker in cost_data and cost_data[ticker] and 
                cost_data[ticker].get('alerts')):
                if not alerts_found:
                    console.print("\n[yellow]Trading Cost Alerts:[/yellow]")
                    alerts_found = True
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
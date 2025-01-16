import click
from .analyzer import ETFAnalyzer
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from . import __version__

console = Console()

METRIC_DESCRIPTIONS = {
    'Alpha (Annual)': 'Risk-adjusted excess return vs benchmark',
    'Beta': 'Sensitivity to market movements',
    'Information Ratio': 'Risk-adjusted active return',
    'Sortino Ratio': 'Return per unit of downside risk',
    'Up Capture': 'Performance in up markets vs benchmark',
    'Down Capture': 'Performance in down markets vs benchmark',
    'Tracking Error': 'Deviation from benchmark returns',
    'Volatility': 'Price movement variability',
    'Sharpe Ratio': 'Return per unit of risk',
    'Max Drawdown': 'Largest peak-to-trough decline',
    'Liquidity Score': 'Trading ease based on volume, spread, and size'
}

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
            analyzer.calculate_performance_metrics()
            
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

        # Create and populate main table
        table = Table(title=f"ETF Analysis: {ticker}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        # Store metrics for descriptions
        metrics_to_describe = []
        
        # Add all rows
        for metric, value in [
            ("Name", analyzer.data['basic']['name']),
            ("Category", analyzer.data['basic']['category']),
            ("Expense Ratio", f"{analyzer.data['basic']['expenseRatio']:.2%}"),
            ("Volatility (Annualized)", f"{analyzer.metrics['volatility']:.2%}"),
            ("Tracking Error", f"{analyzer.metrics['tracking_error']:.2%}"),
            ("Liquidity Score", f"{analyzer.metrics['liquidity_score']:.1f}/100"),
            ("Sharpe Ratio", f"{analyzer.metrics['sharpe_ratio']:.2f}"),
            ("Max Drawdown", f"{analyzer.metrics['max_drawdown']:.2%}"),
            ("Alpha (Annual)", f"{analyzer.metrics['alpha']:.2%}"),
            ("Beta", f"{analyzer.metrics['beta']:.2f}"),
            ("Information Ratio", f"{analyzer.metrics['information_ratio']:.2f}"),
            ("Sortino Ratio", f"{analyzer.metrics['sortino_ratio']:.2f}")
        ]:
            table.add_row(metric, value)
            if metric in METRIC_DESCRIPTIONS:
                metrics_to_describe.append(metric)
        
        # Add capture ratios if available
        if 'capture_ratios' in analyzer.metrics:
            table.add_row("Up Capture", f"{analyzer.metrics['capture_ratios']['up_capture']:.2f}x")
            table.add_row("Down Capture", f"{analyzer.metrics['capture_ratios']['down_capture']:.2f}x")
            metrics_to_describe.extend(["Up Capture", "Down Capture"])

        # Print main table
        console.print(table)

        # Print metric descriptions if any
        if metrics_to_describe:
            console.print("\n[dim]Metric Descriptions:[/dim]")
            for metric in metrics_to_describe:
                if metric in METRIC_DESCRIPTIONS:
                    console.print(f"[dim]• {metric}: {METRIC_DESCRIPTIONS[metric]}[/dim]")

        # Add summary
        findings = _get_summary(analyzer)
        if findings:
            console.print("\n[bold]Key Findings:[/bold]")
            for finding in findings:
                console.print(f"• {finding}")

        if findings:
            console.print("\n[bold]Recommendation:[/bold]")
            console.print(_get_recommendation(analyzer))

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
    
    with console.status("[bold green]Analyzing ETFs...") as status:
        for ticker in tickers:
            if debug:
                console.print(f"[dim]Debug: Analyzing {ticker}...[/dim]")
            table.add_column(ticker.upper(), style="magenta")
            analyzer = ETFAnalyzer(ticker, debug=debug)
            analyzer.collect_basic_info()
            analyzer.collect_performance()
            analyzer.calculate_metrics()
            analyzer.calculate_performance_metrics()
            analyzers[ticker] = analyzer
            if debug:
                console.print(f"[dim]Debug: Completed analysis of {ticker}[/dim]")
    
    # Add rows for each metric
    metrics = [
        ("Expense Ratio", lambda a: f"{a.data['basic'].get('expenseRatio', 0):.2%}"),
        ("Volatility", lambda a: f"{a.metrics['volatility']:.2%}"),
        ("Tracking Error", lambda a: f"{a.metrics['tracking_error']:.2%}"),
        ("Liquidity Score", lambda a: f"{a.metrics['liquidity_score']:.1f}/100"),
        ("Sharpe Ratio", lambda a: f"{a.metrics['sharpe_ratio']:.2f}"),
        ("Max Drawdown", lambda a: f"{a.metrics['max_drawdown']:.2%}"),
        ("Alpha (Annual)", lambda a: f"{a.metrics['alpha']:.2%}"),
        ("Beta", lambda a: f"{a.metrics['beta']:.2f}"),
        ("Information Ratio", lambda a: f"{a.metrics['information_ratio']:.2f}"),
        ("Sortino Ratio", lambda a: f"{a.metrics['sortino_ratio']:.2f}"),
        ("Up Capture", lambda a: f"{a.metrics['capture_ratios']['up_capture']:.2f}x"),
        ("Down Capture", lambda a: f"{a.metrics['capture_ratios']['down_capture']:.2f}x")
    ]
    
    def _get_metric_style(metric, value):
        """Get color style based on metric value"""
        try:
            value = value.replace('[', '').replace(']', '')
            value = float(value.strip('%x').replace(',', ''))
            
            styles = {
                'Alpha (Annual)': lambda v: 'green' if v > 0 else 'red',
                'Information Ratio': lambda v: 'green' if v > 0.5 else 'red' if v < -0.5 else 'yellow',
                'Sharpe Ratio': lambda v: 'green' if v > 1 else 'red' if v < 0 else 'yellow',
                'Volatility': lambda v: 'green' if v < 0.15 else 'red' if v > 0.25 else 'yellow',
                'Max Drawdown': lambda v: 'green' if v > -0.10 else 'red' if v < -0.20 else 'yellow',
                'Expense Ratio': lambda v: 'green' if v < 0.005 else 'red' if v > 0.01 else 'yellow',
                'Liquidity Score': lambda v: 'green' if v > 50 else 'red' if v < 30 else 'yellow',
                'Beta': lambda v: 'green' if 0.8 <= v <= 1.2 else 'yellow' if 0.5 <= v <= 1.5 else 'red',
                'Up Capture': lambda v: 'green' if v > 1 else 'red' if v < 0.8 else 'yellow',
                'Down Capture': lambda v: 'green' if v < 1 else 'red' if v > 1.2 else 'yellow'
            }
            
            if metric in styles:
                return styles[metric](value)
            
        except:
            return None

    for metric_name, metric_func in metrics:
        row = [metric_name]
        for ticker in tickers:
            value = metric_func(analyzers[ticker])
            style = _get_metric_style(metric_name, value)
            # Only add style tags if we got a valid style
            row.append(f"[{style}]{value}[/{style}]" if style else value)
        table.add_row(*row)
    
    console.print(table)

    # Add recommendations for each ETF
    console.print("\n[bold]ETF Recommendations:[/bold]")
    for ticker in tickers:
        recommendation = _get_recommendation(analyzers[ticker])
        findings = _get_summary(analyzers[ticker])
        
        console.print(f"\n[bold]{ticker}:[/bold] {recommendation} ({_get_recommendation_confidence(analyzers[ticker])})")
        if findings:
            console.print("[dim]Key points:[/dim]")
            for finding in findings[:3]:  # Show top 3 findings
                console.print(f"  {finding}")
    
    # Add relative comparison
    best_etf = None
    best_score = -float('inf')
    
    for ticker in tickers:
        score = _calculate_comparison_score(analyzers[ticker])
        if score > best_score:
            best_score = score
            best_etf = ticker
    
    if best_etf:
        console.print(f"\n[bold]Relative Comparison:[/bold]")
        console.print(f"[green]• {best_etf} shows the strongest overall metrics[/green]")
        
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

    # Add summary comparison table
    summary_table = Table(title="Summary Comparison")
    summary_table.add_column("ETF", style="cyan")
    summary_table.add_column("Strengths", style="green")
    summary_table.add_column("Weaknesses", style="red")
    
    for ticker in tickers:
        analyzer = analyzers[ticker]
        strengths = []
        weaknesses = []
        
        # Identify strengths
        if analyzer.metrics['alpha'] > 0:
            strengths.append("Positive alpha")
        if analyzer.metrics['liquidity_score'] > 40:
            strengths.append("Good liquidity")
        if analyzer.data['basic']['expenseRatio'] < 0.007:
            strengths.append("Low cost")
            
        # Identify weaknesses
        if analyzer.metrics['volatility'] > 0.20:
            weaknesses.append("High volatility")
        if analyzer.metrics['max_drawdown'] < -0.15:
            weaknesses.append("Large drawdowns")
        if analyzer.metrics['information_ratio'] < -0.5:
            weaknesses.append("Poor active returns")
            
        summary_table.add_row(
            ticker,
            "\n".join(strengths[:2]) if strengths else "None",
            "\n".join(weaknesses[:2]) if weaknesses else "None"
        )
    
    console.print("\n[bold]Summary:[/bold]")
    console.print(summary_table)

    # Add risk-adjusted rankings with scores and trends
    rankings = {
        'Sharpe': [(t, analyzers[t].metrics['sharpe_ratio'], 'Higher is better') for t in tickers],
        'Information': [(t, analyzers[t].metrics['information_ratio'], 'Above 0.5 is strong') for t in tickers],
        'Overall': [(t, _calculate_comparison_score(analyzers[t]), 'Max score: 100') for t in tickers]
    }
    
    console.print("\n[bold]Risk-Adjusted Rankings:[/bold]")
    for metric, scores in rankings.items():
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        metric_note = scores[0][2]  # Get the note/description
        console.print(f"\n[dim]{metric} Ratio ({metric_note}):[/dim]")
        for i, (t, s, _) in enumerate(sorted_scores):
            color = 'green' if i == 0 else 'yellow' if i == 1 else 'red'
            console.print(f"  {i+1}. [{color}]{t:<6}[/] ({s:>6.2f})")

    if debug:
        console.print("\n[bold]Scoring System:[/bold]")
        for category, (title, factors) in _get_score_explanation().items():
            console.print(f"\n[dim]{title}[/dim]")
            for factor in factors:
                console.print(f"  • {factor}")

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

def _get_summary(analyzer):
    """Generate a summary of key findings"""
    findings = []
    
    # Risk assessment
    if analyzer.metrics['beta'] > 1.2:
        findings.append("[yellow]High market sensitivity[/]")
    if analyzer.metrics['volatility'] > 0.20:
        findings.append("[yellow]High volatility[/]")
    if analyzer.metrics['max_drawdown'] < -0.20:
        findings.append("[red]Large drawdown risk[/]")
        
    # Performance assessment
    if analyzer.metrics['alpha'] < -0.10:
        findings.append("[red]Significant underperformance[/]")
    elif analyzer.metrics['alpha'] > 0.05:
        findings.append("[green]Strong outperformance[/]")
    
    if analyzer.metrics['information_ratio'] < -1.0:
        findings.append("[red]Poor risk-adjusted active returns[/]")
    elif analyzer.metrics['information_ratio'] > 0.5:
        findings.append("[green]Strong risk-adjusted active returns[/]")
        
    # Cost assessment
    costs = analyzer.analyze_trading_costs()
    if costs['Total Cost'] > 0.03:
        findings.append("[yellow]High trading costs[/]")
    if analyzer.data['basic']['expenseRatio'] > 0.009:
        findings.append("[yellow]High expense ratio[/]")
        
    # Liquidity assessment
    if analyzer.metrics['liquidity_score'] < 30:
        findings.append("[red]Poor liquidity[/]")
    
    return findings

def _get_recommendation(analyzer):
    """Generate investment recommendation"""
    score = 0
    reasons = []
    
    # Score different aspects
    if analyzer.metrics['alpha'] > 0:
        score += 2
        reasons.append("positive alpha")
    if analyzer.metrics['sharpe_ratio'] > 1:
        score += 2
        reasons.append("good risk-adjusted returns")
    if analyzer.metrics['liquidity_score'] > 50:
        score += 1
        reasons.append("good liquidity")
    if analyzer.data['basic']['expenseRatio'] < 0.005:
        score += 1
        reasons.append("low costs")
        
    # Generate recommendation
    if score >= 4:
        return "[green]Strong Buy[/]" + (f" ({', '.join(reasons)})" if reasons else "")
    elif score >= 2:
        return "[yellow]Hold[/]" + (f" ({', '.join(reasons)})" if reasons else "")
    else:
        return "[red]Consider Alternatives[/]"

def _calculate_comparison_score(analyzer):
    """Calculate a comparison score for ranking ETFs"""
    score = 0
    
    try:
        # Performance metrics (35%)
        if analyzer.metrics['alpha'] > 0:
            score += 15
        score += min(20, max(-20, analyzer.metrics['information_ratio'] * 10))  # Cap at ±20
        
        # Risk metrics (25%)
        if 0.8 <= analyzer.metrics['beta'] <= 1.2:
            score += 8
        if analyzer.metrics['volatility'] < 0.20:
            score += 8
        if analyzer.metrics['max_drawdown'] > -0.15:
            score += 9
            
        # Cost and liquidity (25%)
        costs = analyzer.analyze_trading_costs()
        if costs['Total Cost'] < 0.02:
            score += 12
        if analyzer.metrics['liquidity_score'] > 40:
            score += 13
            
        # Peer comparison (15%)
        capture = analyzer.metrics.get('capture_ratios', {})
        if capture.get('up_capture', 0) > 1.0:
            score += 8
        if capture.get('down_capture', float('inf')) < 1.0:
            score += 7
            
    except Exception as e:
        if analyzer.debug:
            print(f"Error calculating score: {str(e)}")
        score = 0
        
    return score

def _get_score_explanation():
    """Generate explanation of scoring components"""
    explanations = {
        'Performance': ('Performance (35%)', [
            'Positive alpha (+15)',
            'Information ratio (±20)'
        ]),
        'Risk': ('Risk Management (25%)', [
            'Balanced beta (+8)',
            'Low volatility (+8)',
            'Controlled drawdown (+9)'
        ]),
        'Cost': ('Cost & Liquidity (25%)', [
            'Low total cost (+12)',
            'Good liquidity (+13)'
        ]),
        'Peer': ('Peer Comparison (15%)', [
            'Strong up capture (+8)',
            'Defensive down capture (+7)'
        ])
    }
    return explanations

def _get_recommendation_confidence(analyzer):
    """Calculate confidence level in recommendation"""
    confidence = 0
    factors = 0
    
    # Data quality
    if len(analyzer.data['price_history']) > 200:  # Good history
        confidence += 1
        factors += 1
        
    # Metric consistency
    metrics = [
        analyzer.metrics['sharpe_ratio'],
        analyzer.metrics['information_ratio'],
        analyzer.metrics['sortino_ratio']
    ]
    if all(isinstance(m, (int, float)) for m in metrics):
        confidence += 1
        factors += 1
        
    # Market conditions
    if analyzer.metrics['volatility'] < 0.25:  # Stable market
        confidence += 1
        factors += 1
        
    return f"{'High' if confidence/factors > 0.8 else 'Medium' if confidence/factors > 0.5 else 'Low'} confidence"

if __name__ == '__main__':
    cli() 
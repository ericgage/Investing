from etf_analyzer import ETFAnalyzer

# Basic ETF analysis
def analyze_single_etf():
    # Create analyzer instance
    analyzer = ETFAnalyzer('VOO')
    
    # Collect and analyze data
    analyzer.collect_basic_info()
    analyzer.collect_performance()
    analyzer.calculate_metrics()
    
    # Access metrics
    volatility = analyzer.metrics['volatility']
    tracking_error = analyzer.metrics['tracking_error']
    liquidity_score = analyzer.metrics['liquidity_score']
    
    print(f"Volatility: {volatility:.2%}")
    print(f"Tracking Error: {tracking_error:.2%}")
    print(f"Liquidity Score: {liquidity_score:.1f}/100")

# Compare multiple ETFs
def compare_etfs(tickers=['VOO', 'SPY', 'IVV']):
    results = {}
    for ticker in tickers:
        analyzer = ETFAnalyzer(ticker)
        analyzer.collect_basic_info()
        analyzer.collect_performance()
        analyzer.calculate_metrics()
        results[ticker] = analyzer.metrics
    
    # Compare expense ratios
    for ticker, metrics in results.items():
        print(f"{ticker} Expense Ratio: {analyzer.data['basic']['expenseRatio']:.2%}") 
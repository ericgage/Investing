from etf_analyzer import ETFAnalyzer
import pandas as pd

# Custom validation thresholds
def validate_with_custom_thresholds(ticker):
    analyzer = ETFAnalyzer(ticker)
    analyzer.collect_basic_info()
    
    # Get data from multiple sources
    etf_com_data = analyzer._get_etf_com_metrics()
    yahoo_data = analyzer._get_yahoo_api_metrics()
    
    # Custom validation
    expense_ratio_diff = abs(
        etf_com_data['expense_ratio'] - 
        yahoo_data['expense_ratio']
    )
    
    if expense_ratio_diff > 0.0005:  # 0.05% threshold
        print(f"Warning: Large expense ratio difference: {expense_ratio_diff:.2%}")

# Historical analysis
def analyze_historical_metrics(ticker, periods=['1mo', '3mo', '6mo', '1y']):
    analyzer = ETFAnalyzer(ticker)
    historical_data = analyzer.track_historical_metrics(periods)
    
    # Create DataFrame for analysis
    df = pd.DataFrame(historical_data).T
    print("\nHistorical Metrics:")
    print(df) 

# Custom benchmark analysis
def analyze_with_custom_benchmark(ticker, benchmark):
    """
    Analyze ETF against a custom benchmark
    
    Args:
        ticker (str): ETF ticker to analyze
        benchmark (str): Custom benchmark ticker
    """
    analyzer = ETFAnalyzer(ticker, benchmark_ticker=benchmark)
    analyzer.collect_basic_info()
    analyzer.collect_performance()
    analyzer.calculate_metrics()
    
    print(f"\nAnalyzing {ticker} against {benchmark}:")
    print(f"Tracking Error: {analyzer.metrics['tracking_error']:.2%}")
    
    # Get correlation
    etf_returns = analyzer.data['price_history']['Close'].pct_change().dropna()
    bench_returns = analyzer.data['benchmark_history']['Close'].pct_change().dropna()
    correlation = etf_returns.corr(bench_returns)
    
    print(f"Correlation: {correlation:.2f}")

def analyze_trading_metrics(ticker):
    """
    Analyze real-time trading metrics including bid-ask spread and IIV
    """
    analyzer = ETFAnalyzer(ticker)
    rt_data = analyzer.collect_real_time_data()
    
    if rt_data:
        print(f"\nReal-Time Trading Metrics for {ticker}:")
        print(f"Bid-Ask Spread: ${rt_data['spread']:.3f} ({rt_data['spread_pct']:.3f}%)")
        
        if rt_data['iiv'] is not None:
            premium_discount = ((rt_data['last_price'] - rt_data['iiv']) / rt_data['iiv']) * 100
            print(f"IIV: ${rt_data['iiv']:.2f}")
            print(f"Premium/Discount: {premium_discount:+.2f}%")
            
        # Calculate trading cost metrics
        round_trip_cost = rt_data['spread_pct'] * 2  # Buy and sell
        print(f"Est. Round-Trip Cost: {round_trip_cost:.3f}%")

if __name__ == '__main__':
    # Example usage
    analyze_with_custom_benchmark('QQQ', 'VOO')  # Compare QQQ against VOO 
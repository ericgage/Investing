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
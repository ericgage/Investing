import pytest
from etf_analyzer import ETFAnalyzer
import pandas as pd

def test_full_analysis_flow(mock_etf_data):
    """Test the entire analysis flow"""
    analyzer = ETFAnalyzer('TEST')
    analyzer.data = mock_etf_data
    
    # Add sufficient price history for metrics calculation
    analyzer.data['price_history'] = pd.DataFrame({
        'Close': [100.0 + i*0.01 for i in range(100)],  # 100 days of slightly increasing prices
        'High': [101.0] * 100,
        'Low': [99.0] * 100,
        'Volume': [1000000] * 100
    }, index=pd.date_range(end=pd.Timestamp.now(), periods=100))
    
    # Test metrics calculation
    analyzer.calculate_metrics()
    assert 'volatility' in analyzer.metrics
    assert 'tracking_error' in analyzer.metrics
    
    # Test trading costs
    costs = analyzer.analyze_trading_costs()
    assert costs is not None
    assert 'total' in costs
    
    # Test market maker analysis
    mm_data = analyzer.analyze_market_making()
    assert mm_data is not None
    assert 'quote_presence' in mm_data

@pytest.mark.slow
def test_comparison_flow(mock_etf_data):
    """Test ETF comparison functionality"""
    analyzers = {}
    
    for ticker in ['VOO', 'SPY', 'IVV']:
        analyzer = ETFAnalyzer(ticker)
        analyzer.data = mock_etf_data
        analyzers[ticker] = analyzer
    
    # Compare expense ratios
    expense_ratios = {
        ticker: a.data['basic']['expenseRatio']
        for ticker, a in analyzers.items()
    }
    assert all(er > 0 for er in expense_ratios.values()) 
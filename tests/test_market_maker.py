import pytest
from etf_analyzer import ETFAnalyzer
import pandas as pd

def test_market_maker_metrics(mock_market_data):
    analyzer = ETFAnalyzer('TEST')
    # Set up required data
    analyzer.data = {
        'basic': {'name': 'Test ETF'},
        'intraday': mock_market_data
    }
    
    mm_analysis = analyzer.analyze_market_making()
    assert mm_analysis is not None
    assert 'quote_presence' in mm_analysis

def test_market_depth_calculation(mock_market_data):
    analyzer = ETFAnalyzer('TEST')
    analyzer.data = {
        'basic': {'name': 'Test ETF'},
        'intraday': mock_market_data,
        'price_history': pd.DataFrame({
            'Volume': [1000000] * 100,
            'High': range(100, 200),
            'Low': range(99, 199),
            'Close': range(99, 199),
            'Bid': [100.00] * 100,
            'Ask': [100.02] * 100
        }, index=pd.date_range(start='2024-01-01', periods=100))
    }
    
    mm_analysis = analyzer.analyze_market_making()
    assert mm_analysis is not None
    assert 'depth_score' in mm_analysis
    assert mm_analysis['depth_score'] >= 0 
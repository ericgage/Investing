import pytest
from etf_analyzer import ETFAnalyzer
import pandas as pd

def test_real_time_data_handling(mock_etf_data):
    """Test real-time data collection and validation"""
    analyzer = ETFAnalyzer('TEST')
    analyzer.data = mock_etf_data.copy()
    
    # Test real-time data collection
    rt_data = analyzer.collect_real_time_data()
    assert rt_data is not None
    assert 'bid' in rt_data
    assert 'ask' in rt_data
    assert 'last_price' in rt_data
    assert 'timestamp' in rt_data
    
    # Verify spread calculation
    if rt_data['bid'] and rt_data['ask']:
        spread = rt_data['ask'] - rt_data['bid']
        assert spread >= 0
        assert rt_data['spread'] == spread
        assert rt_data['spread_pct'] == spread / ((rt_data['bid'] + rt_data['ask']) / 2)

def test_missing_iiv_handling():
    """Test handling of missing IIV data"""
    analyzer = ETFAnalyzer('TEST')
    
    # Set up test data without IIV
    analyzer.data = {
        'basic': {
            'name': 'Test ETF',
            'category': 'Test Category',
            'expenseRatio': 0.0003
        },
        'real_time': {
            'bid': 100.0,
            'ask': 100.1,
            'last_price': 100.05,
            'timestamp': pd.Timestamp.now(tz='UTC'),
            'iiv': None  # Missing IIV
        }
    }
    
    # Should not raise error for missing IIV
    rt_data = analyzer.collect_real_time_data()
    assert rt_data is not None
    assert rt_data['iiv'] is None 
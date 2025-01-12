import pytest
from etf_analyzer import ETFAnalyzer
import pandas as pd

def test_premium_discount_calculation(mock_etf_data, mock_browser):
    """Test premium/discount calculation with normal data"""
    analyzer = ETFAnalyzer('TEST')
    analyzer.browser = mock_browser
    
    # Create test data with all required fields
    test_data = mock_etf_data.copy()
    test_data['real_time'] = {
        'last_price': 101.0,  # 1% premium
        'iiv': 100.0,
        'bid': 100.0,
        'ask': 102.0,
        'timestamp': pd.Timestamp.now(tz='UTC')
    }
    analyzer.data = test_data
    
    analysis = analyzer.analyze_premium_discount()
    assert analysis is not None
    assert 'current' in analysis
    assert abs(analysis['current']['premium_discount'] - 1.0) < 0.0001  # Should be ~1% premium

def test_premium_discount_alerts(mock_etf_data, mock_browser):
    """Test alerts for large premium/discount"""
    analyzer = ETFAnalyzer('TEST')
    analyzer.browser = mock_browser
    
    # Create a large premium scenario
    test_data = mock_etf_data.copy()
    test_data['real_time'].update({
        'last_price': 102.0,  # 2% premium
        'iiv': 100.0,
        'bid': 101.0,
        'ask': 103.0
    })
    
    analyzer.data = test_data
    analysis = analyzer.analyze_premium_discount()
    
    assert analysis is not None
    assert len(analysis['alerts']) > 0
    assert any('premium' in alert.lower() for alert in analysis['alerts']) 
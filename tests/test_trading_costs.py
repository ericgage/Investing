import pytest
from etf_analyzer import ETFAnalyzer
import pandas as pd

def test_trading_cost_calculation(mock_etf_data):
    """Test basic trading cost calculation"""
    analyzer = ETFAnalyzer('TEST')
    analyzer.data = mock_etf_data.copy()
    
    # Update real-time data with high spread
    analyzer.data['real_time'].update({
        'bid': 100.0,
        'ask': 100.5,  # 0.5% spread
        'last_price': 100.25
    })
    
    costs = analyzer.analyze_trading_costs()
    assert costs is not None
    assert costs['implicit']['spread_cost'] == 0.0025  # Half of 0.5%
    assert costs['total']['round_trip'] > costs['total']['one_way']

def test_cost_alerts(mock_etf_data, mock_browser):
    """Test cost alerts for high spreads"""
    analyzer = ETFAnalyzer('TEST')
    analyzer.browser = mock_browser
    
    # Create high spread scenario
    test_data = mock_etf_data.copy()
    test_data['real_time'].update({
        'bid': 100.00,
        'ask': 100.50,  # 0.5% spread (high)
        'last_price': 100.25,
        'spread': 0.50,
        'spread_pct': 0.005
    })
    
    analyzer.data = test_data
    costs = analyzer.analyze_trading_costs()
    
    assert costs is not None
    assert len(costs['alerts']) > 0
    assert any('high spread' in alert.lower() for alert in costs['alerts'])

def test_spread_calculation(mock_etf_data, mock_browser):
    """Test spread calculation with different market conditions"""
    analyzer = ETFAnalyzer('TEST')
    analyzer.browser = mock_browser
    
    # Test normal spread
    test_data = mock_etf_data.copy()
    test_data['real_time'].update({
        'bid': 100.00,
        'ask': 100.02,  # 0.02% spread (normal)
        'last_price': 100.01,
        'spread': 0.02,
        'spread_pct': 0.0002
    })
    
    analyzer.data = test_data
    costs = analyzer.analyze_trading_costs()
    
    assert costs is not None
    assert costs['implicit']['spread_cost'] < 0.001  # Less than 0.1%
    assert len(costs['alerts']) == 0  # No alerts for normal spread 
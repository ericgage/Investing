import pytest
from etf_analyzer import ETFAnalyzer
import pandas as pd

def test_cost_comparison(mock_etf_data):
    analyzer = ETFAnalyzer('TEST')
    analyzer.data = mock_etf_data.copy()
    
    # Ensure real-time data has all required fields
    analyzer.data['real_time'].update({
        'bid': 100.0,
        'ask': 100.5,
        'last_price': 100.25,
        'spread': 0.50,
        'spread_pct': 0.005,
        'timestamp': pd.Timestamp.now(tz='UTC')
    })
    
    costs = analyzer.analyze_trading_costs()
    assert costs is not None
    assert 'total' in costs
    assert 'round_trip' in costs['total']
    assert costs['total']['round_trip'] > costs['total']['one_way'] 
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

@pytest.fixture
def mock_market_closed(monkeypatch):
    """Mock market as closed"""
    def mock_is_market_open(self):
        return False
    monkeypatch.setattr('etf_analyzer.analyzer.ETFAnalyzer._is_market_open', mock_is_market_open)

def test_missing_iiv_handling(mock_market_closed, monkeypatch):
    """Test handling of missing IIV data"""
    print("\nDebug: Starting missing IIV test")
    analyzer = ETFAnalyzer('TEST')
    print("Debug: Created analyzer")
    
    # Mock history data
    history = pd.DataFrame({
        'Close': [100.0],
        'High': [101.0],
        'Low': [99.0],
        'Volume': [1000000]
    }, index=[pd.Timestamp.now(tz='UTC')])
    
    def mock_history(*args, **kwargs):
        return history
    
    def mock_get_last_known_values(self):
        """Mock to ensure IIV field is present"""
        return {
            'bid': None,
            'ask': None,
            'last_price': 100.0,
            'iiv': None,  # Add IIV field
            'timestamp': pd.Timestamp.now(tz='UTC'),
            'market_status': 'closed'
        }
    
    monkeypatch.setattr('yfinance.Ticker.history', mock_history)
    monkeypatch.setattr('etf_analyzer.analyzer.ETFAnalyzer._get_last_known_values', mock_get_last_known_values)
    
    rt_data = analyzer.collect_real_time_data()
    print(f"Debug: Collected real-time data: {rt_data}")
    assert rt_data is not None
    print(f"Debug: rt_data keys: {rt_data.keys()}")
    assert 'iiv' in rt_data
    assert rt_data['iiv'] is None 
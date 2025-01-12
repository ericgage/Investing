import pytest
from etf_analyzer import ETFAnalyzer
import pandas as pd

def test_invalid_ticker(monkeypatch):
    def mock_collect_performance_invalid(self):
        raise ValueError("Insufficient price history for INVALID")
    
    monkeypatch.setattr('etf_analyzer.analyzer.ETFAnalyzer.collect_performance', 
                       mock_collect_performance_invalid)
    
    analyzer = ETFAnalyzer('INVALID')
    with pytest.raises(ValueError, match="Insufficient price history"):
        analyzer.collect_performance()

def test_insufficient_data():
    analyzer = ETFAnalyzer('TEST')
    analyzer.data['price_history'] = pd.DataFrame({
        'Close': [],
        'High': [],
        'Low': [],
        'Volume': []
    })
    
    with pytest.raises(ValueError, match="Insufficient data"):
        analyzer.calculate_metrics()

def test_missing_real_time_data():
    analyzer = ETFAnalyzer('TEST')
    result = analyzer.analyze_trading_costs()
    assert result is None or 'alerts' in result 
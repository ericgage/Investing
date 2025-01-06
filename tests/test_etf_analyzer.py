import pytest
from etf_analyzer import ETFAnalyzer

def test_etf_analyzer_initialization():
    analyzer = ETFAnalyzer("SPY")
    assert analyzer.ticker == "SPY"
    assert isinstance(analyzer.data, dict)

def test_collect_basic_info():
    analyzer = ETFAnalyzer("SPY")
    analyzer.collect_basic_info()
    assert 'basic' in analyzer.data
    
def test_calculate_metrics():
    analyzer = ETFAnalyzer("SPY")
    analyzer.collect_performance()
    analyzer.calculate_metrics()
    assert 'volatility' in analyzer.metrics 
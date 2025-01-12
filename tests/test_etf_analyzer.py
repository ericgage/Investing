import pytest
from etf_analyzer import ETFAnalyzer

def test_etf_analyzer_initialization():
    analyzer = ETFAnalyzer("SPY")
    assert analyzer.ticker == "SPY"
    assert isinstance(analyzer.data, dict)

def test_collect_basic_info():
    analyzer = ETFAnalyzer("TEST")
    analyzer.data = {
        'basic': {
            'expenseRatio': 0.0003,
            'totalAssets': 1000000000,
        }
    }
    analyzer.collect_basic_info()
    assert 'basic' in analyzer.data
    assert 'expenseRatio' in analyzer.data['basic']
    
def test_calculate_metrics():
    analyzer = ETFAnalyzer("SPY")
    analyzer.collect_performance()
    analyzer.calculate_metrics()
    assert 'volatility' in analyzer.metrics 

def test_tracking_error():
    """Test tracking error calculation"""
    # Test with same ticker as benchmark (should be 0)
    analyzer = ETFAnalyzer("SPY", benchmark_ticker="SPY")
    analyzer.collect_performance()
    error = analyzer._calculate_tracking_error()
    assert abs(error) < 1e-10  # Should be very close to 0
    
    # Test with different benchmark
    analyzer = ETFAnalyzer("QQQ", benchmark_ticker="SPY")
    analyzer.collect_performance()
    error = analyzer._calculate_tracking_error()
    assert error > 0.0  # Should have some tracking error
    assert error < 1.0  # But not too large

def test_liquidity_score():
    # Test with highly liquid ETF
    analyzer = ETFAnalyzer("SPY")
    analyzer.collect_performance()
    score = analyzer._calculate_liquidity_score()
    assert score > 0
    assert score <= 100
    
    # Test relative liquidity
    spy_analyzer = ETFAnalyzer("SPY")
    small_etf_analyzer = ETFAnalyzer("VTHR")  # Less liquid ETF
    
    spy_analyzer.collect_performance()
    small_etf_analyzer.collect_performance()
    
    spy_score = spy_analyzer._calculate_liquidity_score()
    small_etf_score = small_etf_analyzer._calculate_liquidity_score()
    
    assert spy_score > small_etf_score  # SPY should be more liquid 
import pytest
from etf_analyzer import ETFAnalyzer
import pandas as pd

@pytest.fixture
def mock_analyzer(monkeypatch):
    """Mock ETFAnalyzer for tests"""
    def mock_init(self, ticker, benchmark_ticker='SPY', debug=False):
        self.ticker = ticker
        self.benchmark = benchmark_ticker
        self.debug = debug
        self.data = {'basic': {}, 'price_history': None}
        self.metrics = {}
    
    monkeypatch.setattr('etf_analyzer.analyzer.ETFAnalyzer.__init__', mock_init)

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
    
def test_calculate_metrics(mock_analyzer):
    """Test metric calculations"""
    analyzer = ETFAnalyzer("SPY", benchmark_ticker="SPY")
    print(f"Debug: Created analyzer with benchmark={analyzer.benchmark}")
    analyzer.collect_performance()
    analyzer.calculate_metrics()
    assert 'volatility' in analyzer.metrics
    assert 'tracking_error' in analyzer.metrics
    assert 'liquidity_score' in analyzer.metrics

def test_tracking_error(mock_analyzer):
    """Test tracking error calculation"""
    analyzer = ETFAnalyzer("SPY", benchmark_ticker="SPY")
    print(f"Debug: Created analyzer with benchmark={analyzer.benchmark}")
    analyzer.collect_performance()
    assert analyzer._calculate_tracking_error() == 0.0  # Same ticker should have 0 tracking error
    
    # Test with different benchmark
    analyzer = ETFAnalyzer("QQQ", benchmark_ticker="SPY")
    analyzer.collect_performance()
    error = analyzer._calculate_tracking_error()
    assert error > 0.0  # Should have some tracking error
    assert error < 1.0  # But not too large

def test_liquidity_score():
    """Test liquidity score calculation"""
    # Set up SPY analyzer with high liquidity
    spy_analyzer = ETFAnalyzer("SPY")
    spy_analyzer.data['basic'] = {
        'totalAssets': 1_000_000_000,  # $1B AUM
        'expenseRatio': 0.0003
    }
    spy_analyzer.data['price_history'] = pd.DataFrame({
        'Volume': [1_000_000] * 100  # High volume
    })
    spy_analyzer.data['real_time'] = {
        'spread_pct': 0.001  # Tight spread
    }
    
    # Set up VTHR analyzer with lower liquidity
    small_etf_analyzer = ETFAnalyzer("VTHR")
    small_etf_analyzer.data['basic'] = {
        'totalAssets': 100_000_000,  # $100M AUM
        'expenseRatio': 0.0003
    }
    small_etf_analyzer.data['price_history'] = pd.DataFrame({
        'Volume': [100_000] * 100  # Lower volume
    })
    small_etf_analyzer.data['real_time'] = {
        'spread_pct': 0.005  # Wider spread
    }
    
    spy_score = spy_analyzer._calculate_liquidity_score()
    small_etf_score = small_etf_analyzer._calculate_liquidity_score()
    
    assert spy_score > small_etf_score  # SPY should be more liquid 
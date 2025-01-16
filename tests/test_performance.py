"""Tests for performance metrics calculations"""
import pytest
import pandas as pd
import numpy as np
from etf_analyzer import ETFAnalyzer

@pytest.fixture
def sample_price_data():
    """Create sample price data for testing"""
    dates = pd.date_range(start='2023-01-01', periods=252)
    np.random.seed(42)
    
    # Generate more realistic returns
    market_returns = np.random.normal(0.0004, 0.01, 252)  # ~10% annual return
    etf_returns = market_returns * 1.1 + np.random.normal(0, 0.002, 252)  # Slightly higher return with noise
    
    # Convert returns to prices
    market_prices = pd.Series((1 + market_returns).cumprod(), index=dates)
    etf_prices = pd.Series((1 + etf_returns).cumprod(), index=dates)
    
    return {
        'etf': pd.DataFrame({'Close': etf_prices}),
        'benchmark': pd.DataFrame({'Close': market_prices})
    }

def test_alpha_calculation(sample_price_data):
    """Test Jensen's Alpha calculation"""
    analyzer = ETFAnalyzer('TEST')
    analyzer.data['price_history'] = sample_price_data['etf']
    analyzer.data['benchmark_history'] = sample_price_data['benchmark']
    
    alpha = analyzer._calculate_alpha(analyzer.data['price_history']['Close'].pct_change().dropna())
    assert isinstance(alpha, float)
    assert -0.2 <= alpha <= 0.2  # Alpha typically within ±20%
    
    # Test benchmark case
    analyzer.ticker = analyzer.benchmark
    alpha = analyzer._calculate_alpha(analyzer.data['price_history']['Close'].pct_change().dropna())
    assert alpha == 0.0  # Alpha should be 0 for benchmark

def test_beta_calculation(sample_price_data):
    """Test Beta calculation"""
    analyzer = ETFAnalyzer('TEST')
    analyzer.data['price_history'] = sample_price_data['etf']
    analyzer.data['benchmark_history'] = sample_price_data['benchmark']
    
    returns = analyzer.data['price_history']['Close'].pct_change().dropna()
    beta = analyzer._calculate_beta(returns)
    
    assert isinstance(beta, float)
    assert -2.0 <= beta <= 2.0  # Beta should be reasonable

def test_sortino_ratio(sample_price_data):
    """Test Sortino ratio calculation"""
    analyzer = ETFAnalyzer('TEST')
    analyzer.data['price_history'] = sample_price_data['etf']
    
    returns = analyzer.data['price_history']['Close'].pct_change().dropna()
    sortino = analyzer._calculate_sortino_ratio(returns)
    
    assert isinstance(sortino, float)
    assert -5.0 <= sortino <= 5.0  # Sortino should be reasonable 

def test_capture_ratios(sample_price_data):
    """Test up/down market capture ratios"""
    analyzer = ETFAnalyzer('TEST')
    analyzer.data['price_history'] = sample_price_data['etf']
    analyzer.data['benchmark_history'] = sample_price_data['benchmark']
    
    returns = analyzer.data['price_history']['Close'].pct_change().dropna()
    capture = analyzer._calculate_capture_ratios(returns)
    
    assert isinstance(capture, dict)
    assert 'up_capture' in capture
    assert 'down_capture' in capture
    assert 0.5 <= capture['up_capture'] <= 1.5  # Should be reasonably close to 1
    assert 0.5 <= abs(capture['down_capture']) <= 1.5 
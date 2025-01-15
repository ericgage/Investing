import pytest
from etf_analyzer import ETFAnalyzer
import pandas as pd
from selenium.common.exceptions import WebDriverException
from requests.exceptions import RequestException
from etf_analyzer.browser import BrowserSession

def test_browser_error_simple(monkeypatch):
    """Test browser error handling with minimal mocking"""
    # Mock yfinance to ensure we need ETF.com data
    class MockTicker:
        def __init__(self, *args, **kwargs):  # Accept constructor args
            pass
            
        @property
        def info(self):
            return {
                'expenseRatio': None,
                'annualReportExpenseRatio': None,
                'totalExpenseRatio': None,
                'longName': 'Test ETF',
                'category': 'Test Category'
            }
    
    def mock_get_metrics(self):
        raise WebDriverException("Browser failed")
    
    monkeypatch.setattr('etf_analyzer.analyzer.yf.Ticker', MockTicker)
    monkeypatch.setattr('etf_analyzer.analyzer.ETFAnalyzer._get_etf_com_metrics', mock_get_metrics)
    
    analyzer = ETFAnalyzer('SPY')
    with pytest.raises(RuntimeError, match="Browser failed"):  # Match the exact error message
        analyzer.collect_basic_info()

def test_api_error_simple(monkeypatch):
    """Test API error handling with minimal mocking"""
    class MockTicker:
        @property
        def info(self):
            return {
                'expenseRatio': 0.0003,  # Provide expense ratio to avoid ETF.com lookup
                'longName': 'Test ETF',
                'category': 'Test Category'
            }
        
        def history(self, *args, **kwargs):
            raise RequestException("API failed")
    
    monkeypatch.setattr('etf_analyzer.analyzer.yf.Ticker', MockTicker)
    
    analyzer = ETFAnalyzer('SPY')
    with pytest.raises(RuntimeError):
        analyzer.collect_performance()

def test_browser_initialization_error(monkeypatch):
    """Test handling of browser initialization failures"""
    class MockTicker:
        def __init__(self, *args, **kwargs):  # Accept constructor args
            pass
            
        @property
        def info(self):
            return {
                'expenseRatio': None,
                'annualReportExpenseRatio': None,
                'totalExpenseRatio': None,
                'longName': 'Test ETF',
                'category': 'Test Category'
            }
    
    def mock_etf_metrics(self):
        raise WebDriverException("Failed to initialize browser")
    
    monkeypatch.setattr('etf_analyzer.analyzer.yf.Ticker', MockTicker)  # Use correct import path
    monkeypatch.setattr('etf_analyzer.analyzer.ETFAnalyzer._get_etf_com_metrics', mock_etf_metrics)
    
    analyzer = ETFAnalyzer('SPY')
    with pytest.raises(RuntimeError, match="Failed to initialize browser"):
        analyzer.collect_basic_info()

def test_api_timeout_error(monkeypatch):
    """Test handling of API timeout errors"""
    class MockTicker:
        def __init__(self, *args, **kwargs):
            pass
            
        def history(self, *args, **kwargs):
            raise RequestException("API request timed out")
            
        @property
        def info(self):
            return {}
    
    monkeypatch.setattr('yfinance.Ticker', MockTicker)
    
    analyzer = ETFAnalyzer('SPY')
    with pytest.raises(RuntimeError, match="Failed to fetch price history"):
        analyzer.collect_performance()

def test_malformed_data_handling():
    """Test handling of malformed data"""
    analyzer = ETFAnalyzer('SPY')
    
    # Test with missing columns
    analyzer.data['price_history'] = pd.DataFrame({
        'Close': [100.0] * 100,  # Missing required columns
        'High': [101.0] * 100,
        'Low': [99.0] * 100
    }, index=pd.date_range(start='2024-01-01', periods=100))
    
    with pytest.raises(ValueError, match="Missing required columns"):
        analyzer.validate_data()

def test_data_consistency_checks():
    """Test data consistency validation"""
    analyzer = ETFAnalyzer('SPY')
    
    # Create data with consistent lengths first
    dates = pd.date_range(start='2024-01-01', periods=100, tz='UTC')
    data = {
        'Close': [100.0] * 100,
        'High': [101.0] * 100,
        'Low': [99.0] * 100,
        'Volume': [1000000] * 100
    }
    analyzer.data['price_history'] = pd.DataFrame(data, index=dates)
    
    # Create inconsistency by directly modifying the DataFrame
    analyzer.data['price_history'] = pd.DataFrame({
        'Close': [100.0] * 100,
        'High': [101.0] * 100,
        'Low': [99.0] * 100,
        'Volume': [1000000] * 99 + [None]  # Add None at the end
    }, index=dates)
    
    with pytest.raises(ValueError, match="Inconsistent data lengths"):
        analyzer.validate_data()

def test_benchmark_data_errors(mock_browser, monkeypatch):
    """Test benchmark-related error handling"""
    analyzer = ETFAnalyzer('TEST', benchmark_ticker='INVALID')
    with pytest.raises(RuntimeError) as excinfo:
        analyzer.collect_performance()
    # Accept either error message format
    assert any(msg in str(excinfo.value) for msg in [
        "Failed to fetch benchmark data",
        "Failed to fetch price history"
    ])

def test_real_time_data_validation():
    """Test real-time data validation"""
    analyzer = ETFAnalyzer('SPY')
    
    # Test with invalid bid/ask
    analyzer.data['real_time'] = {
        'bid': 100.0,
        'ask': 99.0,  # Ask lower than bid
        'last_price': 99.5,
        'timestamp': pd.Timestamp.now()
    }
    
    with pytest.raises(ValueError, match="Invalid bid/ask prices"):
        analyzer.validate_real_time_data()
    
    # Test with stale data
    old_timestamp = pd.Timestamp.now() - pd.Timedelta(hours=2)
    analyzer.data['real_time'] = {
        'bid': 100.0,
        'ask': 101.0,
        'last_price': 100.5,
        'timestamp': old_timestamp
    }
    
    with pytest.raises(ValueError, match="Stale data"):
        analyzer.validate_real_time_data() 
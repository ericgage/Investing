import pytest
from unittest.mock import Mock
import yfinance as yf
from selenium import webdriver
from requests.exceptions import RequestException
from selenium.common.exceptions import WebDriverException
import pandas as pd

# Add mock ETFDataCache class
class MockETFDataCache:
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        self.cache[key] = value

@pytest.fixture(autouse=True)
def mock_cache(monkeypatch):
    """Mock the ETFDataCache import"""
    monkeypatch.setattr('etf_analyzer.analyzer.ETFDataCache', MockETFDataCache)

@pytest.fixture
def mock_etf_data():
    """Mock ETF data for testing"""
    return {
        'basic': {
            'name': 'Test ETF',
            'category': 'Test Category',
            'expenseRatio': 0.0003,
            'totalAssets': 1000000000,
            'description': 'Test ETF Description',
            'average_spread': 0.0002
        },
        'real_time': {
            'bid': 100.0,
            'ask': 100.5,
            'last_price': 100.25,
            'iiv': 100.0,
            'spread': 0.50,
            'spread_pct': 0.005,
            'timestamp': pd.Timestamp.now(tz='UTC')
        },
        'price_history': pd.DataFrame({
            'Close': [100.0] * 100,
            'High': [101.0] * 100,
            'Low': [99.0] * 100,
            'Volume': [1000000] * 100
        }, index=pd.date_range(start='2024-01-01', periods=100, tz='UTC'))
    }

@pytest.fixture
def mock_market_data():
    """Mock market data for testing"""
    return pd.DataFrame({
        'Close': [100.0] * 100,
        'High': [101.0] * 100,
        'Low': [99.0] * 100,
        'Volume': [1000000] * 100,
        'Bid': [99.5] * 100,
        'Ask': [100.5] * 100
    }, index=pd.date_range(start='2024-01-01', periods=100, tz='UTC'))

@pytest.fixture
def mock_browser():
    """Mock browser session for testing"""
    class MockDriver:
        def get(self, url):
            print(f"Debug: mock_browser.get called with URL: {url}")
            pass
            
        @property
        def page_source(self):
            print("Debug: mock_browser.page_source called")
            html = """<html>
<head><title>TEST ETF Report | ETF.com</title></head>
<body>
<div class="ticker-header">TEST</div>
<div class="fund-info">
    <div class="metric">
        <div class="label">Expense Ratio</div>
        <div class="value">0.03%</div>
    </div>
    <div class="metric">
        <div class="label">AUM</div>
        <div class="value">$1.2B</div>
    </div>
    <div class="metric">
        <div class="label">Average Volume</div>
        <div class="value">1M</div>
    </div>
    <div class="metric">
        <div class="label">IIV</div>
        <div class="value">100.00</div>
    </div>
    <div class="metric">
        <div class="label">Spread</div>
        <div class="value">0.50%</div>
    </div>
</div>
</body>
</html>"""
            return html
    
    return MockDriver() 

@pytest.fixture(autouse=True)
def mock_analyzer(monkeypatch, mock_browser):
    """Automatically patch ETFAnalyzer to use mock browser"""
    def mock_init(self, ticker, benchmark_ticker="SPY"):
        self.ticker = ticker
        self.benchmark_ticker = benchmark_ticker
        self.data = {}
        self.metrics = {}
        self.browser = mock_browser
        self.cache = MockETFDataCache()
    
    monkeypatch.setattr('etf_analyzer.analyzer.ETFAnalyzer.__init__', mock_init) 

@pytest.fixture(autouse=True)
def mock_yfinance(monkeypatch):
    """Mock yfinance for all tests"""
    # Create a single date range to be used by all history calls
    end_date = pd.Timestamp.now(tz='UTC')
    dates = pd.date_range(end=end_date, periods=100)
    
    class MockTicker:
        def __init__(self, ticker):
            self.ticker = ticker
            self.info = {
                'longName': 'Test ETF',
                'category': 'Test Category',
                'expenseRatio': 0.0003,
                'totalAssets': 1000000000 if ticker == 'SPY' else 100000000
            }
            
        def history(self, *args, **kwargs):
            # Different price patterns for different ETFs
            if self.ticker == 'QQQ':
                # QQQ has more volatile returns
                prices = [100.0 * (1 + i * 0.02) for i in range(100)]
                volume = 500000
            else:
                # SPY and others have steady prices
                prices = [100.0] * 100
                volume = 1000000 if self.ticker == 'SPY' else 100000
                
            return pd.DataFrame({
                'Close': prices,
                'High': [p * 1.01 for p in prices],
                'Low': [p * 0.99 for p in prices],
                'Volume': [volume] * 100
            }, index=dates)  # Use the shared date range
    
    monkeypatch.setattr('yfinance.Ticker', MockTicker) 

@pytest.fixture(autouse=True)
def mock_console(monkeypatch):
    """Mock rich console for tests"""
    class MockConsole:
        def print(self, table):
            # Convert rich table to plain text for tests
            for row in table.rows:
                print(f"{row[0]}: {row[1]}")
    
    monkeypatch.setattr('rich.console.Console', lambda: MockConsole()) 
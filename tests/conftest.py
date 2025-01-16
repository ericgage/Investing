import pytest
from etf_analyzer import ETFAnalyzer

@pytest.fixture
def debug_analyzer():
    """Create ETFAnalyzer instance with debug enabled"""
    return ETFAnalyzer('SPY', debug=True)
    
@pytest.fixture
def silent_analyzer():
    """Create ETFAnalyzer instance with debug disabled"""
    return ETFAnalyzer('SPY', debug=False)
    
@pytest.fixture
def mock_chrome_driver(monkeypatch):
    """Mock Chrome WebDriver"""
    from selenium.webdriver.chrome.webdriver import WebDriver
    from selenium.webdriver.remote.command import Command
    
    class MockCommandExecutor:
        def execute(self, command, params=None):
            return {'status': 0, 'value': None}
    
    class MockChrome(WebDriver):
        def __init__(self, *args, **kwargs):
            # Skip parent init but keep inheritance
            self.session_id = 'mock_session'
            self.command_executor = MockCommandExecutor()
            
        def get(self, url):
            return "<html>Mock page</html>"
            
        def quit(self):
            pass
            
        @property
        def page_source(self):
            return "<html>Mock page</html>"
            
        def execute_cdp_cmd(self, cmd, params=None):
            """Mock CDP command execution with proper responses"""
            if cmd == "Browser.getVersion":
                return {
                    'userAgent': 'Mozilla/5.0 (Mock) Chrome',
                    'jsVersion': 'mock',
                    'product': 'mock'
                }
            return {'value': None}
            
    monkeypatch.setattr('selenium.webdriver.Chrome', MockChrome)
    return MockChrome 
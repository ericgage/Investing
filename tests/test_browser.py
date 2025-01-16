import pytest
from etf_analyzer.browser import BrowserSession
from selenium import webdriver

def test_browser_session_tracking():
    """Test browser session success tracking"""
    browser = BrowserSession()
    
    # Test with mock driver
    with browser as session:
        assert session is not None
        assert browser.driver is None  # Should be None until get() is called
        
        # Now test get()
        driver = browser.get('http://example.com')
        assert driver is not None
        assert browser.driver is not None

def test_browser_modes(mock_chrome_driver):
    """Test both browser modes"""
    browser = BrowserSession()
    
    # Test headless Chrome initialization
    page_source = browser.get("http://example.com")
    assert "Mock page" in page_source
    assert browser.page_source == page_source  # Test property access
    
    # Test cleanup
    browser.__exit__(None, None, None)
    assert browser.driver is None
    assert browser.page_source is None  # Test property after cleanup

def test_browser_caching():
    """Test browser caching behavior"""
    browser = BrowserSession()
    
    # Test browser reuse
    first_source = browser.get("http://example.com")
    second_source = browser.get("http://example.com")
    
    # Should get same page content
    assert "Example Domain" in first_source
    assert "Example Domain" in second_source
    
    # Cleanup
    browser.__exit__(None, None, None) 
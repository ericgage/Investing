# Browser Session Migration Guide

## Updating Code to Use Hybrid Browser

### 1. Update Browser Usage

Before:
```python
# Old way - always using Selenium
response = self.browser.get(url)
data = self._parse_page(response.page_source)
```

After:
```python
# New way - specify JS requirements
response = self.browser.get(url, require_js=needs_javascript)
if needs_javascript:
    data = self._parse_page(response.page_source)
else:
    data = self._parse_page(response.text)
```

### 2. Add Caching Where Appropriate

Before:
```python
def get_etf_data(self, ticker):
    url = f"https://example.com/{ticker}"
    response = self.browser.get(url)
    return self._parse_data(response)
```

After:
```python
def get_etf_data(self, ticker):
    url = f"https://example.com/{ticker}"
    # Cache ETF data for 1 hour
    response = self.browser.get(url, require_js=True, use_cache=True)
    return self._parse_data(response)
```

### 3. Handle Both Response Types

```python
def _parse_data(self, response):
    """Handle both Selenium and Requests responses"""
    if isinstance(response, webdriver.Chrome):
        content = response.page_source
    else:
        content = response.text
    
    return BeautifulSoup(content, 'html.parser')
```

### 4. Update Error Handling

```python
try:
    response = self.browser.get(url, require_js=True)
except selenium.common.exceptions.WebDriverException:
    self._debug("Selenium error - falling back to requests")
    response = self.browser.get(url, require_js=False)
except requests.exceptions.RequestException:
    self._debug("Request failed")
    return None 
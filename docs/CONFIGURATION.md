# Configuration Guide

## Environment Variables

```bash
# Rate limiting
ETF_ANALYZER_RATE_LIMIT=10  # requests per minute
ETF_ANALYZER_CACHE_DIR=.cache  # cache directory path

# Browser automation
ETF_ANALYZER_BROWSER_TIMEOUT=10  # seconds
ETF_ANALYZER_USER_AGENT="Custom User Agent String"

# Debug settings
ETF_ANALYZER_DEBUG=True  # enable debug mode
ETF_ANALYZER_LOG_LEVEL=DEBUG  # logging level
```

## Configuration File

Create `config.yaml` in your project root:

```yaml
# Data sources
sources:
  etf_com:
    enabled: true
    priority: 1
    rate_limit: 5
  yahoo_finance:
    enabled: true
    priority: 2
    
# Validation thresholds
thresholds:
  expense_ratio:
    warning: 0.0005  # 0.05%
    error: 0.001     # 0.1%
  aum:
    warning: 0.10    # 10%
    error: 0.25      # 25%
  volume:
    warning: 0.15    # 15%
    error: 0.30      # 30%

# Cache settings
cache:
  enabled: true
  directory: .cache
  ttl: 86400  # 24 hours

# Browser settings
browser:
  headless: true
  timeout: 10
  retries: 3
```

## Logging Configuration

Create `logging.yaml`:

```yaml
version: 1
formatters:
  simple:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    formatter: simple
    level: INFO
  file:
    class: logging.FileHandler
    filename: etf_analyzer.log
    formatter: simple
    level: DEBUG
loggers:
  etf_analyzer:
    level: INFO
    handlers: [console, file]
    propagate: false
```

## Custom Metrics Configuration

Create `metrics.yaml`:

```yaml
metrics:
  liquidity_score:
    volume_weight: 0.4
    spread_weight: 0.3
    assets_weight: 0.3
  tracking_error:
    window: 252  # trading days
    min_periods: 200
  volatility:
    annualization: 252
    rolling_window: 21
```

## Browser Automation Setup

### Required Dependencies
- selenium: Web browser automation
- selenium-stealth: Anti-detection measures
- ChromeDriver: Browser interface

### ChromeDriver Installation

1. **macOS (using Homebrew)**:
```bash
brew install --cask chromedriver
```

2. **Ubuntu/Debian**:
```bash
sudo apt install chromium-chromedriver
```

3. **Windows**:
- Download ChromeDriver from: https://chromedriver.chromium.org/
- Add to PATH or specify location in config

### Configuration Options

```python
# config/browser.py
BROWSER_CONFIG = {
    'headless': True,           # Run without visible window
    'stealth': True,            # Enable anti-detection
    'timeout': 10,              # Page load timeout (seconds)
    'retry_attempts': 3,        # Failed request retries
    'user_agent': None,         # Custom user agent (or None for default)
}
```

### Troubleshooting

1. **Version Mismatch**
```bash
# Check Chrome version
google-chrome --version

# Install matching ChromeDriver version
```

2. **Permission Issues**
```bash
# macOS/Linux
chmod +x /path/to/chromedriver

# Windows
# Run as Administrator
```

3. **Common Errors**:
- WebDriverException: Update ChromeDriver
- SessionNotCreated: Version mismatch
- ConnectionRefused: Driver not running 
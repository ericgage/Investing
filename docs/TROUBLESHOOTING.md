# Troubleshooting Guide

## Common Issues

### ETF.com Access Issues

1. **403 Forbidden Error**
```
Error: ETF.com returned status code 403
```
Solutions:
- Verify ChromeDriver installation
- Clear browser cache
- Check rate limiting
- Use debug mode for more info

2. **Parsing Errors**
```
Error: could not convert string to float
```
Solutions:
- Check HTML structure changes
- Update parsing patterns
- Use debug logging
- Check data format

### Browser Automation

1. **ChromeDriver Issues**
```
Error: ChromeDriver not found
```
Solutions:
- Verify PATH settings
- Reinstall ChromeDriver
- Check version compatibility
- Remove quarantine (macOS)

2. **Permission Issues**
```
Error: Operation not permitted
```
Solutions:
- Run with sudo (Linux/macOS)
- Check security settings
- Allow in system preferences
- Update permissions

### Data Validation

1. **Large Differences**
```
Warning: AUM difference > 25%
```
Solutions:
- Check data freshness
- Verify source reliability
- Compare timestamps
- Use alternative sources

2. **Missing Data**
```
Warning: Could not find expense ratio
```
Solutions:
- Check data sources
- Verify ticker symbol
- Use alternative sources
- Check cache status

## Debug Mode

Enable debug logging:
```bash
etf-analyzer analyze VOO --debug
```

## Support

1. Open an issue with:
   - Full error message
   - OS and version
   - Steps to reproduce
   - Debug output

2. Include environment info:
```bash
etf-analyzer --version
python --version
pip list
```

# Advanced Troubleshooting Guide

## Data Collection Issues

### ETF.com Scraping Failures
```python
# Debug ETF.com scraping
analyzer = ETFAnalyzer('VOO')
analyzer.debug_etf_com_scraping()  # New debug method
```

Common issues:
1. Rate limiting (Solution: Adjust rate limits)
2. HTML structure changes (Solution: Update parsing patterns)
3. Network connectivity (Solution: Check proxy settings)

### Real-Time Data Issues
```python
# Verify data freshness
analyzer.verify_data_freshness()  # New verification method
```

Solutions:
1. Check market hours
2. Verify API connectivity
3. Clear cache if needed

## Trading Cost Analysis

### High Cost Alerts
```python
# Detailed cost breakdown
analyzer.debug_cost_components()  # New debug method
```

Investigation steps:
1. Compare with historical costs
2. Check market conditions
3. Verify calculation inputs

### Premium/Discount Analysis
```python
# Debug premium/discount calculation
analyzer.debug_premium_discount()  # New debug method
```

Common issues:
1. Stale IIV data
2. Market volatility
3. Corporate actions 
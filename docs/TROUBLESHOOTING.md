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
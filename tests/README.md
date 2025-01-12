# ETF Analyzer Tests

## Overview
This directory contains tests for the ETF Analyzer package. The tests are organized by functionality and use pytest as the testing framework.

## Test Structure

### Fixtures (`conftest.py`)
- `mock_etf_data`: Provides mock ETF data for testing, including:
  - Price history
  - Basic information
  - Real-time data
  - Intraday data
- `mock_market_data`: Provides mock market maker data

### Test Categories

#### Basic Functionality (`test_etf_analyzer.py`)
- Initialization
- Basic info collection
- Metric calculations
- Tracking error
- Liquidity scoring

#### Trading Costs (`test_trading_costs.py`)
- Cost calculation
- Spread analysis
- Cost alerts
- Trading impact

#### Real-Time Data (`test_real_time.py`)
- Data collection
- Bid/ask handling
- IIV processing
- Missing data handling

#### Market Making (`test_market_maker.py`)
- Quote presence
- Spread stability
- Market depth
- Price continuity

#### Error Handling (`test_error_handling.py`)
- Invalid tickers
- Insufficient data
- Missing data handling
- API errors

#### Integration (`test_integration.py`)
- Full analysis flow
- Multi-ETF comparison
- Data validation

## Running Tests

### Basic Usage
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_trading_costs.py

# Run specific test
pytest tests/test_trading_costs.py::test_spread_calculation
```

### Coverage Reports
```bash
# Run with coverage report
pytest --cov=etf_analyzer

# Generate HTML coverage report
pytest --cov=etf_analyzer --cov-report=html
```

### Test Markers
- `slow`: Marks tests that take longer to run
```bash
# Run without slow tests
pytest -m "not slow"
```

## Mock Data

### Price History
```python
{
    'Close': [100, 101, 99, 102],
    'High': [102, 103, 100, 103],
    'Low': [99, 100, 98, 101],
    'Volume': [1000000, 1200000, 900000, 1100000]
}
```

### Real-Time Data
```python
{
    'bid': 100.00,
    'ask': 100.02,
    'last_price': 100.01,
    'spread': 0.02,
    'spread_pct': 0.0002,  # 0.02%
    'iiv': 100.00
}
```

## Adding New Tests

1. Create test file in `tests/` directory
2. Import required modules and fixtures
3. Use descriptive test names
4. Add appropriate assertions
5. Update documentation

Example:
```python
def test_new_feature(mock_etf_data):
    """Test description here"""
    analyzer = ETFAnalyzer('TEST')
    analyzer.data = mock_etf_data
    
    result = analyzer.new_feature()
    assert result is not None
    assert 'expected_key' in result
```

## Test Design Principles

1. **Isolation**: Each test should be independent
2. **Clarity**: Use descriptive names and docstrings
3. **Coverage**: Test both success and failure cases
4. **Maintainability**: Use fixtures for shared data
5. **Performance**: Mark slow tests appropriately

## Common Issues

### Missing Data
If tests fail due to missing data, check:
- Mock data fixtures in `conftest.py`
- Required fields in test data
- Data initialization in tests

### API Errors
For tests involving external APIs:
- Use mock responses
- Handle rate limiting
- Test error conditions

### Coverage Gaps
To improve coverage:
- Add edge cases
- Test error handling
- Include integration tests

## Contributing

1. Add tests for new features
2. Update existing tests as needed
3. Ensure all tests pass
4. Update documentation
5. Submit pull request 
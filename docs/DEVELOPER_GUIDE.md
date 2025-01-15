# Developer Guide

## Development Setup

1. **Environment Setup**
```bash
# Create development environment
python3 -m venv etfa-dev
source etfa-dev/bin/activate
pip install -r requirements-dev.txt
```

2. **Pre-commit Hooks**
```bash
pre-commit install
```

## Code Structure

```
etf_analyzer/
├── __init__.py
├── analyzer.py     # Core analysis logic
├── browser.py     # Browser automation
├── cli.py         # Command line interface
└── utils.py       # Helper functions

tests/
├── __init__.py
└── test_*.py      # Test files
```

## Testing

1. **Running Tests**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=etf_analyzer

# Run specific test file
pytest tests/test_analyzer.py
```

2. **Mock Data**
- Use `tests/fixtures/` for mock responses
- Use `@pytest.fixture` for common test data

## Code Style

1. **Type Hints**
```python
def calculate_metric(data: pd.DataFrame) -> float:
    """
    Calculate a metric from DataFrame.
    
    Args:
        data: Price history data
        
    Returns:
        float: Calculated metric
    """
    return float(data.std())
```

2. **Documentation**
- Use Google-style docstrings
- Include examples in docstrings
- Document exceptions

## Pull Request Process

1. Create feature branch
2. Write tests
3. Update documentation
4. Run linters
5. Submit PR with description

## Release Process

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create release branch
4. Tag release
5. Build and publish 

## Market Impact Analysis

### What is Market Impact?
Market Impact is the effect that a trade has on the market price of a security. When executing a large order, the price typically moves adversely against the trader:
- Buy orders tend to push prices up
- Sell orders tend to push prices down

### Impact Factors

Market impact is calculated using several factors:

1. **Base Impact Factor (0.1 or 10%)**
```python
impact_factor = 0.1  # 10% of spread for normal trades
market_impact = spread_cost * impact_factor
```

2. **Volume-Based Scaling**
```python
# Trade size relative to average daily volume (ADV)
IMPACT_THRESHOLDS = {
    0.01: 0.1,   # 1% of ADV: normal impact (10% of spread)
    0.05: 0.2,   # 5% of ADV: doubled impact (20% of spread)
    0.10: 0.4,   # 10% of ADV: quadrupled impact (40% of spread)
    0.20: 0.8    # 20% of ADV: severe impact (80% of spread)
}
```

3. **Liquidity Adjustments**
- High liquidity (score > 80): impact reduced by 20%
- Medium liquidity (score 50-80): standard impact
- Low liquidity (score < 50): impact increased by 20%

### Example Calculations

1. **Small Trade (1% ADV)**
```python
# For an ETF with:
spread = 0.10%           # 10 basis points spread
adv = 1,000,000 shares  # Average daily volume
trade_size = 10,000     # 1% of ADV

base_impact = spread * 0.1
adjusted_impact = base_impact * (trade_size / adv / 0.01)
# Result: ~0.01% price impact
```

2. **Large Trade (10% ADV)**
```python
trade_size = 100,000    # 10% of ADV

base_impact = spread * 0.4
adjusted_impact = base_impact * (trade_size / adv / 0.10)
# Result: ~0.04% price impact
```

### Market Impact Alerts

The system generates alerts based on estimated impact:
```python
if market_impact > 0.002:  # 0.2% threshold
    alerts.append(f"High market impact: {market_impact:.3%}")
```

### Best Practices

1. **Trade Size Considerations**
- Keep individual trades below 1% ADV when possible
- Split large orders into smaller chunks
- Use time-weighted average price (TWAP) for large orders

2. **Timing Considerations**
- Avoid trading at market open/close
- Consider higher impacts during low-volume periods
- Monitor unusual market conditions

3. **Liquidity Monitoring**
- Regular tracking of liquidity scores
- Adjustment of impact estimates based on market conditions
- Consideration of historical liquidity patterns 
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
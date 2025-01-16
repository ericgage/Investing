# Test Migration Guide

## Migrating to Fixture-Based Tests

### 1. Choose the Right Fixture

- `base_analyzer`: For basic functionality tests
  ```python
  def test_basic_operation(base_analyzer):
      result = base_analyzer.calculate_metrics()
      assert result is not None
  ```

- `debug_analyzer`: For data flow and processing tests
  ```python
  def test_data_processing(debug_analyzer):
      data = debug_analyzer.collect_real_time_data()
      assert data['market_status'] == 'open'
  ```

- `silent_analyzer`: For error handling tests
  ```python
  def test_error_case(silent_analyzer):
      with pytest.raises(ValueError):
          silent_analyzer.validate_data()
  ```

### 2. Update Test Files

1. Add fixture to test parameters:
```python
# Before
def test_something():
    analyzer = ETFAnalyzer('TEST')

# After
def test_something(base_analyzer):
    analyzer = base_analyzer
```

2. Remove manual analyzer creation:
```python
# Remove these lines
analyzer = ETFAnalyzer('TEST')
analyzer.debug = True
```

3. Update assertions if needed:
```python
# Before
assert analyzer.debug is True

# After
assert analyzer._debug is not None
```

### 3. Special Cases

1. **Tests that modify debug behavior:**
```python
def test_debug_switching(base_analyzer):
    analyzer = base_analyzer
    analyzer.debug = not analyzer.debug  # Toggle debug
```

2. **Tests that need clean analyzer:**
```python
@pytest.fixture
def clean_analyzer():
    return ETFAnalyzer('TEST', debug=False)

def test_clean_state(clean_analyzer):
    assert clean_analyzer.data == {}
```

### 4. Migration Checklist

- [ ] Import fixtures in conftest.py
- [ ] Update test parameters
- [ ] Remove direct ETFAnalyzer instantiation
- [ ] Update debug-related assertions
- [ ] Test with pytest -v to verify 
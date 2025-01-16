import pytest
from etf_analyzer import ETFAnalyzer
import pandas as pd

def test_basic_validation(debug_analyzer):
    """Example of using debug_analyzer fixture"""
    analyzer = debug_analyzer
    analyzer.data['basic'] = {'expenseRatio': 0.0009}
    costs = analyzer.analyze_trading_costs()
    assert costs['Expense Ratio'] == 0.0009

def test_validation_error(silent_analyzer):
    """Example of using silent_analyzer for error cases"""
    analyzer = silent_analyzer
    # Force validation error by setting insufficient data
    analyzer.data['price_history'] = pd.DataFrame({'Close': [], 'Volume': []})
    with pytest.raises(ValueError, match="Insufficient data"):
        analyzer.validate_metrics() 
"""
Test suite for ETF Analyzer validation and error handling.
"""
import pytest
from etf_analyzer import ETFAnalyzer
import pandas as pd

def test_basic_validation(debug_analyzer):
    """Test basic cost analysis with debug output"""
    analyzer = debug_analyzer
    analyzer.data['basic'] = {'expenseRatio': 0.0009}
    costs = analyzer.analyze_trading_costs()
    assert costs['Expense Ratio'] == 0.0009

def test_validation_error(silent_analyzer):
    """Test validation error handling with insufficient data"""
    analyzer = silent_analyzer
    analyzer.data['price_history'] = pd.DataFrame({'Close': [], 'Volume': []})
    with pytest.raises(ValueError, match="Insufficient data"):
        analyzer.validate_metrics() 
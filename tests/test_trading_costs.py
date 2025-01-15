import pytest
from etf_analyzer.analyzer import ETFAnalyzer
import pandas as pd

@pytest.fixture
def mock_etf():
    analyzer = ETFAnalyzer('TEST')
    # Mock basic data
    analyzer.data['basic'] = {'expenseRatio': 0.005}  # 0.5% expense ratio
    return analyzer

def test_trading_costs_expense_ratio_only(mock_etf):
    """Test when only expense ratio is available"""
    costs = mock_etf.analyze_trading_costs()
    
    assert costs['explicit']['expense_ratio'] == 0.005
    assert costs['implicit']['spread_cost'] is None
    assert costs['implicit']['market_impact'] is None
    assert costs['total']['one_way'] == 0.005
    assert costs['total']['round_trip'] == 0.01
    assert "No real-time data available" in costs['alerts'][0]

def test_trading_costs_with_real_time_data(mock_etf):
    """Test with real-time bid/ask data"""
    # Mock real-time data
    mock_etf.data['real_time'] = {
        'bid': 100.0,
        'ask': 100.10,
    }
    
    # Add required price history for volume calculation
    mock_etf.data['price_history'] = pd.DataFrame({
        'Volume': [1000000] * 30  # 30 days of volume data
    })
    
    costs = mock_etf.analyze_trading_costs()
    
    # Spread cost should be half the spread percentage
    expected_spread_cost = ((100.10 - 100.0) / 100.05) / 2
    expected_market_impact = expected_spread_cost * 0.1
    
    assert costs['explicit']['expense_ratio'] == 0.005
    assert pytest.approx(costs['implicit']['spread_cost']) == expected_spread_cost
    assert pytest.approx(costs['implicit']['market_impact']) == expected_market_impact
    assert len(costs['alerts']) == 0

def test_trading_costs_without_volume_data(mock_etf):
    """Test handling of missing volume data"""
    mock_etf.data['real_time'] = {
        'bid': 100.0,
        'ask': 100.10,
    }
    # Don't add volume data
    
    costs = mock_etf.analyze_trading_costs()
    
    expected_spread_cost = ((100.10 - 100.0) / 100.05) / 2
    expected_market_impact = expected_spread_cost * 0.1
    
    assert costs['explicit']['expense_ratio'] == 0.005
    assert pytest.approx(costs['implicit']['spread_cost']) == expected_spread_cost
    assert pytest.approx(costs['implicit']['market_impact']) == expected_market_impact
    assert "Using default market impact estimate" in costs['alerts'][0]

def test_trading_costs_with_invalid_data(mock_etf):
    """Test handling of invalid bid/ask data"""
    # Mock invalid real-time data
    mock_etf.data['real_time'] = {
        'bid': 0,
        'ask': 0,
    }
    
    costs = mock_etf.analyze_trading_costs()
    
    assert costs['explicit']['expense_ratio'] == 0.005
    assert costs['implicit']['spread_cost'] is None
    assert costs['implicit']['market_impact'] is None
    assert costs['total']['one_way'] == 0.005
    assert costs['total']['round_trip'] == 0.01
    assert "No real-time bid/ask data available" in costs['alerts'][0] 
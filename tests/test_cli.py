import pytest
from click.testing import CliRunner
from etf_analyzer.cli import cli
import pandas as pd

@pytest.fixture
def mock_analyzer(monkeypatch):
    """Mock ETFAnalyzer for CLI tests"""
    def mock_init(self, ticker, benchmark_ticker='SPY', debug=False):
        self.ticker = ticker
        self.benchmark = benchmark_ticker
        self.debug = debug
        self.data = {
            'basic': {'expenseRatio': 0.0009},
            'price_history': pd.DataFrame({'Close': [100] * 100}),
            'validation': {
                'expense_ratio': {'our': 0.0009, 'external': 0.001},
                'aum': {'our': 1e9, 'external': 1.1e9},
                'volume': {'our': 1e6, 'external': 1.1e6}
            }
        }
        self.metrics = {}
        self.browser = None
        self.cache = None
    
    def mock_validate(self):
        """Mock validation method"""
        return {
            'expense_ratio': {'match': True, 'diff': 0.0001},
            'aum': {'match': True, 'diff': 0.1},
            'volume': {'match': True, 'diff': 0.1}
        }
    
    monkeypatch.setattr('etf_analyzer.analyzer.ETFAnalyzer.__init__', mock_init)
    monkeypatch.setattr('etf_analyzer.analyzer.ETFAnalyzer.validate_metrics', mock_validate)

def test_analyze_basic():
    """Test basic analyze command"""
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', 'SPY'])
    assert result.exit_code == 0
    assert any(text in result.output for text in [
        'ETF Analysis: SPY',
        'Trading Cost Analysis'
    ])

def test_analyze_with_benchmark():
    """Test analyze with benchmark option"""
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', 'QQQ', '--benchmark', 'SPY'])
    assert result.exit_code == 0
    assert 'Using SPY as benchmark' in result.output
    assert 'Tracking Error' in result.output

def test_analyze_with_options():
    """Test analyze with additional options"""
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', 'SPY'])
    assert result.exit_code == 0
    assert 'Basic Information' in result.output
    assert 'Expense Ratio' in result.output
    assert 'Volatility' in result.output 

def test_analyze_verbose():
    """Test verbose analysis output"""
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', 'SPY', '--verbose'])
    assert result.exit_code == 0
    assert 'Detailed Liquidity Analysis' in result.output
    assert 'Volume Score' in result.output
    assert 'Spread Score' in result.output
    assert 'Asset Score' in result.output 

def test_analyze_validate():
    """Test validation output"""
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', 'SPY', '--validate'])
    assert result.exit_code == 0
    assert 'Validation Results' in result.output
    assert 'Our Value' in result.output
    assert 'External Value' in result.output
    assert 'Difference' in result.output 

def test_analyze_history():
    """Test historical metrics output"""
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', 'SPY', '--history'])
    assert result.exit_code == 0
    assert 'Historical Metrics' in result.output
    assert '3mo' in result.output
    assert '6mo' in result.output
    assert '1y' in result.output
    # Check for metric columns
    assert 'Volatility' in result.output
    assert 'Sharpe Ratio' in result.output
    assert 'Max Drawdown' in result.output 

def test_validation_color_coding(mock_validation_data):
    """Test validation output color coding"""
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', 'SPY', '--validate'])
    assert result.exit_code == 0
    
    output = result.output
    
    # Test for differences with more flexible matching
    assert any(f"{val}%" in output for val in ["0.000", "0.0"])  # Expense Ratio
    assert any(f"{val}%" in output for val in ["20.0", "20"])    # AUM
    assert any(f"{val}%" in output for val in ["100.0", "100"])  # Volume
    
    # Test for specific values
    assert any(s in output for s in [
        "$1,000,000,000",  # Our AUM
        "$1.0B",          # Alternative format
        "1,000,000"       # Volume
    ])
    
    # Test for notes and icons (if they appear)
    # Check for split messages
    assert all(s in output for s in [
        "⚠️ Warning:",
        "Volume differs",
        "significantly",
        "check",
        "market conditions"
    ])
    assert all(s in output for s in [
        "ℹ️ Note:",
        "AUM varies",
        "between",
        "sources"
    ]) 
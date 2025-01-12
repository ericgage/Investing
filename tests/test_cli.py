import pytest
from click.testing import CliRunner
from etf_analyzer.cli import cli

def test_analyze_basic(mock_browser):
    """Test basic ETF analysis command"""
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', 'TEST'])  # Use TEST instead of VOO to match mock data
    assert result.exit_code == 0
    assert 'ETF Analysis: TEST' in result.output

def test_analyze_with_benchmark(mock_browser):
    """Test ETF analysis with custom benchmark"""
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', 'TEST', '--benchmark', 'SPY'])  # Use TEST
    assert result.exit_code == 0
    assert 'ETF Analysis: TEST' in result.output

def test_analyze_with_options(mock_browser):
    """Test ETF analysis with all options"""
    runner = CliRunner()
    result = runner.invoke(cli, [
        'analyze', 'TEST',  # Use TEST to match mock data
        '--benchmark', 'SPY'
    ])
    assert result.exit_code == 0
    assert 'ETF Analysis: TEST' in result.output 
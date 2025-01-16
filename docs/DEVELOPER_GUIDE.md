# ETF Analyzer Developer Guide

## Overview
ETF Analyzer is a Python tool for analyzing ETF performance, costs, and metrics. It provides comprehensive analysis of ETFs including performance metrics, risk assessment, trading costs, and peer comparisons.

## Development Setup
1. Create a virtual environment:
```bash
python -m venv etfa
source etfa/bin/activate  # or `etfa\Scripts\activate` on Windows
```

2. Install in development mode:
```bash
pip install -e .
```

3. Run tests:
```bash
pytest
```

## Code Structure
- `etf_analyzer/`: Main package directory
  - `analyzer.py`: Core analysis functionality
  - `browser.py`: Web scraping utilities
  - `cli.py`: Command-line interface
  - `utils.py`: Helper functions

## Key Features

### Performance Metrics
- Alpha: Risk-adjusted excess return
- Beta: Market sensitivity
- Information Ratio: Active return per unit of risk
- Sharpe Ratio: Risk-adjusted return
- Sortino Ratio: Downside risk-adjusted return
- Up/Down Capture: Market cycle performance

### Risk Metrics
- Volatility: Price movement variability
- Tracking Error: Deviation from benchmark
- Maximum Drawdown: Largest peak-to-trough decline
- Beta: Market sensitivity measure

### Trading Costs
- Expense Ratio: Fund management fees
- Bid-Ask Spread: Trading friction cost
- Market Impact: Price effect of trading
- Total Cost: Combined trading expenses

### Liquidity Analysis
- Volume Score: Trading volume assessment
- Spread Score: Bid-ask spread evaluation
- Asset Score: Fund size consideration
- Overall Liquidity: Combined liquidity measure

## Command Line Interface

### Single ETF Analysis
```bash
etfa analyze TICKER [OPTIONS]
```
Options:
- `--verbose`: Show detailed metrics
- `--validate`: Compare with external sources
- `--history`: Show historical metrics
- `--costs`: Show trading cost analysis
- `--debug`: Enable debug output

### ETF Comparison
```bash
etfa compare TICKER1 TICKER2 [TICKER3...] [OPTIONS]
```
Options:
- `--costs`: Show trading cost comparison
- `--debug`: Enable debug output

## Testing
- Use pytest for all tests
- Mock external dependencies
- Test both success and error cases
- Include docstrings in test files

### Test Categories
1. Performance Metrics
2. Risk Metrics
3. Cost Analysis
4. Data Collection
5. Error Handling

## Contributing
1. Create a feature branch
2. Add tests for new functionality
3. Run full test suite
4. Submit pull request

## Scoring System
The tool uses a 100-point scoring system:
- Performance (35%): Alpha and Information Ratio
- Risk Management (25%): Beta, Volatility, Drawdown
- Cost & Liquidity (25%): Trading costs and liquidity
- Peer Comparison (15%): Up/Down capture ratios

## Recommendations
Recommendations are provided with confidence levels:
- Strong Buy: Score ≥ 4
- Hold: Score ≥ 2
- Consider Alternatives: Score < 2

Confidence levels (High/Medium/Low) are based on:
- Data quality (history length)
- Metric consistency
- Market conditions 
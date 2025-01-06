# ETF Analyzer

A Python package for analyzing Exchange-Traded Funds (ETFs), providing tools for gathering data, analyzing performance, and calculating key metrics.

## Installation

### Initial Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/etf-analyzer.git
cd etf-analyzer
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python3 -m venv etfa

# Activate virtual environment
# On macOS/Linux:
source etfa/bin/activate
# On Windows:
etfa\Scripts\activate
```

3. Install the package:
```bash
# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Updating the Package
If you've made changes to the code or pulled updates:

1. Ensure your virtual environment is activated:
```bash
source etfa/bin/activate  # macOS/Linux
etfa\Scripts\activate     # Windows
```

2. Uninstall current version:
```bash
pip uninstall etf-analyzer
```

3. Reinstall the updated version:
```bash
pip install -e .
```

4. (Optional) Update dependencies:
```bash
pip install -r requirements.txt --upgrade
```

## Architecture

```mermaid
graph TD
    CLI[CLI Interface] --> Analyzer[ETF Analyzer Core]
    Analyzer --> DataSource[Data Sources]
    Analyzer --> Metrics[Metrics Calculator]
    DataSource --> YFinance[Yahoo Finance API]
    Metrics --> Volatility[Volatility]
    Metrics --> TrackingError[Tracking Error]
    Metrics --> Liquidity[Liquidity Score]
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Analyzer
    participant YFinance
    
    User->>CLI: Input ETF ticker
    CLI->>Analyzer: Create analyzer instance
    Analyzer->>YFinance: Request ETF data
    YFinance-->>Analyzer: Return price history
    YFinance-->>Analyzer: Return basic info
    Analyzer->>Analyzer: Calculate metrics
    Analyzer-->>CLI: Return results
    CLI-->>User: Display formatted results
```

## Entity Relationship

```mermaid
erDiagram
    ETF {
        string ticker
        string name
        string category
        float expense_ratio
    }
    ETF ||--o{ PriceHistory : has
    ETF ||--o{ BasicInfo : has
    ETF ||--o{ Metrics : calculates
    ETF ||--o{ Benchmark : tracks
    PriceHistory ||--|{ DailyPrice : contains
    Metrics ||--|{ VolatilityScore : includes
    Metrics ||--|{ TrackingError : includes
    Metrics ||--|{ LiquidityScore : includes
```

## Data Sources

### Yahoo Finance API
The project uses the `yfinance` library to fetch ETF data from Yahoo Finance. This provides:
- Historical price data
- Trading volume
- Basic ETF information
- Expense ratios
- Assets under management (when available)

### Data Reliability
Yahoo Finance data is generally reliable but may have occasional gaps or delays. The package includes error handling to manage these cases.

## Calculations and Metrics

### 1. Volatility
```python
volatility = price_data.std() * np.sqrt(252)  # Annualized
```
- Measures price variation using standard deviation
- Annualized by multiplying by sqrt(252) trading days
- Higher values indicate more price uncertainty
- Typical range: 10-30% for most ETFs

### 2. Tracking Error
```python
return_differences = etf_returns - benchmark_returns
tracking_error = return_differences.std() * np.sqrt(252)
```
- Measures how closely ETF follows its benchmark
- Lower values indicate better benchmark tracking
- Typical range: 0.1-2% for index ETFs

### 3. Liquidity Score (0-100)
Combines three components:
1. Volume Score (40%):
   ```python
   volume_score = min(40, (avg_volume / 1000000) * 4)
   ```
   - Higher trading volume = better liquidity
   - 4 points per million shares traded

2. Spread Score (30%):
   ```python
   spread_score = max(0, 30 - spread_percentage * 10)
   ```
   - Tighter spreads = lower trading costs
   - Uses high-low range as spread proxy

3. Asset Base Score (30%):
   ```python
   asset_score = min(30, (assets / 1000000000) * 3)
   ```
   - Larger funds typically more liquid
   - 3 points per billion in assets

## Interpreting Results

### Volatility
- <15%: Low volatility, suitable for conservative investors
- 15-25%: Moderate volatility, typical for broad market ETFs
- >25%: High volatility, may require risk tolerance

### Tracking Error
- <0.5%: Excellent benchmark tracking
- 0.5-1%: Good tracking, typical for most index ETFs
- >1%: High tracking error, may indicate active management

### Liquidity Score
- 80-100: Highly liquid, suitable for all traders
- 50-80: Moderately liquid, watch trading costs
- <50: Limited liquidity, use limit orders

## Usage Examples

### Basic Analysis
```bash
etf-analyzer analyze VOO
```

### Detailed Analysis
```bash
# Show detailed breakdown of metrics
etf-analyzer analyze VOO --verbose

# Compare with external data sources
etf-analyzer analyze VOO --validate

# Compare different data providers
etf-analyzer analyze VOO --sources

# Show historical metrics
etf-analyzer analyze VOO --history

# Combine options
etf-analyzer analyze VOO --verbose --validate --history
```

### Comparison Analysis
```bash
etf-analyzer compare VOO SPY QQQ
```

### Custom Benchmark
```bash
etf-analyzer analyze QQQ --benchmark SPY
```

## Validation Methods

### External Data Sources
The analyzer validates metrics against multiple sources:
1. ETF.com
2. Yahoo Finance API
3. Fund provider websites

### Metric Validation
Each metric is validated using:
- Multiple data sources
- Different calculation methods
- Historical consistency checks

### Validation Metrics
| Metric | Validation Method | Typical Difference |
|--------|------------------|-------------------|
| Expense Ratio | Provider websites | < 0.01% |
| Volatility | Multiple timeframes | < 2% |
| Tracking Error | Rolling windows | < 0.5% |
| Liquidity | Market depth data | Varies |

### Interpreting Validation Results
- **Small Differences** (<1%): Normal variation in calculation methods
- **Medium Differences** (1-5%): Investigate data sources
- **Large Differences** (>5%): Potential data issues

## Data Sources Comparison

### Primary Sources
1. **Yahoo Finance (yfinance)**
   - Real-time and historical prices
   - Basic ETF information
   - Trading volume

2. **ETF.com**
   - Expense ratios
   - Fund details
   - Holdings information

3. **Provider Websites**
   - Official expense ratios
   - Detailed holdings
   - Fund documentation

### Source Reliability
| Source | Pros | Cons |
|--------|------|------|
| yfinance | Real-time, Free | API limitations |
| ETF.com | Comprehensive | Web scraping needed |
| Providers | Authoritative | Different formats |

## Best Practices

1. Trading Considerations
   - Use limit orders for ETFs with low liquidity scores
   - Consider trading during market hours for better pricing
   - Monitor tracking error for index-based strategies

2. Analysis Tips
   - Compare similar ETFs before investing
   - Consider expense ratios alongside tracking error
   - Monitor liquidity for large positions

3. Risk Management
   - Use volatility metrics for position sizing
   - Consider correlation with existing holdings
   - Monitor tracking error for index-based strategies

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


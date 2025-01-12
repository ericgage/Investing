# Visualization Guide

## Cost Visualization

### Trading Cost Heatmap
```python
import seaborn as sns
import matplotlib.pyplot as plt

def plot_cost_heatmap(tickers):
    # Collect cost data
    costs = {}
    for ticker in tickers:
        analyzer = ETFAnalyzer(ticker)
        costs[ticker] = analyzer.analyze_trading_costs()
    
    # Create heatmap data
    data = pd.DataFrame({
        ticker: {
            'Spread Cost': d['implicit']['spread_cost'],
            'Market Impact': d['implicit']['market_impact'],
            'Total Cost': d['total']['round_trip']
        } for ticker, d in costs.items()
    })
    
    # Plot heatmap
    plt.figure(figsize=(10, 6))
    sns.heatmap(data, annot=True, fmt='.3%', cmap='RdYlGn_r')
    plt.title('ETF Trading Cost Comparison')
    plt.show()
```

### Premium/Discount History
```python
def plot_premium_discount_history(ticker, days=30):
    analyzer = ETFAnalyzer(ticker)
    history = analyzer.get_premium_discount_history(days)
    
    plt.figure(figsize=(12, 6))
    plt.plot(history.index, history.values, label='Premium/Discount')
    plt.axhline(y=0, color='r', linestyle='--')
    plt.fill_between(history.index, -0.25, 0.25, alpha=0.2, color='g')
    plt.title(f'{ticker} Premium/Discount History')
    plt.ylabel('Premium/Discount (%)')
    plt.legend()
    plt.show()
``` 
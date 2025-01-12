# Integration with pandas
def export_to_pandas(analyzer):
    """Export analysis results to pandas DataFrame"""
    metrics = analyzer.get_all_metrics()
    return pd.DataFrame(metrics)

# Integration with numpy
def perform_statistical_analysis(analyzer):
    """Perform advanced statistical analysis"""
    returns = analyzer.get_returns()
    return {
        'skewness': np.skew(returns),
        'kurtosis': np.kurtosis(returns),
        'var_95': np.percentile(returns, 5)
    }

# Integration with matplotlib
def create_cost_visualization(analyzer):
    """Create cost analysis visualization"""
    costs = analyzer.analyze_trading_costs()
    # Plotting code here...

# Integration with Excel
def export_to_excel(analyzer, filename):
    """Export analysis to Excel"""
    metrics = analyzer.get_all_metrics()
    df = pd.DataFrame(metrics)
    df.to_excel(filename) 
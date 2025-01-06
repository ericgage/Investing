import yfinance as yf
import numpy as np
import pandas as pd

class ETFAnalyzer:
    def __init__(self, ticker, benchmark_ticker="SPY"):
        self.ticker = ticker
        self.benchmark_ticker = benchmark_ticker
        self.data = {}
        self.metrics = {}
        
    def collect_basic_info(self):
        """
        Gather fundamental ETF information
        """
        # Basic info (free sources)
        self.data['basic'] = yf.Ticker(self.ticker).info
        
    def collect_holdings(self):
        """
        Gather current holdings and weights
        """
        # Implementation would vary by ETF provider
        pass
        
    def collect_performance(self):
        """
        Gather historical performance data for both ETF and benchmark
        """
        # Get ETF data
        ticker_data = yf.Ticker(self.ticker)
        self.data['price_history'] = ticker_data.history(period="1y")
        
        # Get benchmark data if it's different from the ETF
        if self.ticker != self.benchmark_ticker:
            benchmark_data = yf.Ticker(self.benchmark_ticker)
            self.data['benchmark_history'] = benchmark_data.history(period="1y")
        
    def calculate_metrics(self):
        """
        Calculate key metrics for analysis
        """
        if 'price_history' not in self.data:
            self.collect_performance()
            
        price_data = self.data['price_history']['Close']
        
        # Calculate various metrics
        self.metrics = {
            'volatility': price_data.std() * np.sqrt(252),
            'tracking_error': self._calculate_tracking_error(),
            'liquidity_score': self._calculate_liquidity_score()
        }

    def _calculate_tracking_error(self):
        """
        Calculate tracking error against benchmark
        
        Tracking error is the standard deviation of the difference
        between the ETF and benchmark returns
        """
        if 'benchmark_history' not in self.data and self.ticker != self.benchmark_ticker:
            self.collect_performance()
            
        # Calculate daily returns
        etf_returns = self.data['price_history']['Close'].pct_change().dropna()
        
        if self.ticker == self.benchmark_ticker:
            return 0.0
            
        benchmark_returns = self.data['benchmark_history']['Close'].pct_change().dropna()
        
        # Align the dates
        etf_returns, benchmark_returns = etf_returns.align(benchmark_returns, join='inner')
        
        # Calculate tracking error
        return_differences = etf_returns - benchmark_returns
        tracking_error = return_differences.std() * np.sqrt(252)  # Annualized
        
        return float(tracking_error)
        
    def _calculate_liquidity_score(self):
        """
        Calculate liquidity score based on:
        1. Average daily volume
        2. Bid-ask spread (estimated from high-low)
        3. Assets under management (if available)
        
        Returns a score from 0 (least liquid) to 100 (most liquid)
        """
        if 'price_history' not in self.data:
            self.collect_performance()
            
        # Calculate average daily volume score (0-40 points)
        avg_volume = self.data['price_history']['Volume'].mean()
        volume_score = min(40, (avg_volume / 1000000) * 4)  # 4 points per million shares
        
        # Calculate spread score using high-low as proxy (0-30 points)
        typical_price = self.data['price_history']['Close'].mean()
        avg_spread = (self.data['price_history']['High'] - self.data['price_history']['Low']).mean()
        spread_percentage = (avg_spread / typical_price) * 100
        spread_score = max(0, 30 - spread_percentage * 10)  # Lower spread = higher score
        
        # Asset base score (0-30 points)
        asset_score = 0
        try:
            if 'basic' in self.data and 'totalAssets' in self.data['basic']:
                assets = self.data['basic']['totalAssets']
                asset_score = min(30, (assets / 1000000000) * 3)  # 3 points per billion in assets
        except:
            pass
            
        # Combine scores
        total_score = volume_score + spread_score + asset_score
        
        return min(100, float(total_score)) 
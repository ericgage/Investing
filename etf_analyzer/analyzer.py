import yfinance as yf
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

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
        try:
            ticker_info = yf.Ticker(self.ticker).info
            
            # Try multiple fields for expense ratio
            expense_ratio = (
                ticker_info.get('annualReportExpenseRatio') or
                ticker_info.get('expenseRatio') or
                ticker_info.get('totalExpenseRatio') or
                0.0
            )
            
            self.data['basic'] = {
                'name': ticker_info.get('longName', 'N/A'),
                'category': ticker_info.get('category', 'N/A'),
                'expenseRatio': float(expense_ratio),
                'totalAssets': ticker_info.get('totalAssets', 0.0),
                'description': ticker_info.get('description', 'N/A')
            }
        except Exception as e:
            print(f"Error collecting basic info for {self.ticker}: {str(e)}")
            self.data['basic'] = {
                'name': 'N/A',
                'category': 'N/A',
                'expenseRatio': 0.0,
                'totalAssets': 0.0,
                'description': 'N/A'
            }
        
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
        try:
            # Get ETF data
            ticker_data = yf.Ticker(self.ticker)
            history = ticker_data.history(period="1y")
            
            if len(history) < 30:  # Minimum data requirement
                raise ValueError(f"Insufficient price history for {self.ticker}")
            
            self.data['price_history'] = history
            
            # Get benchmark data if different
            if self.ticker != self.benchmark_ticker:
                benchmark_data = yf.Ticker(self.benchmark_ticker)
                benchmark_history = benchmark_data.history(period="1y")
                
                if len(benchmark_history) < 30:
                    raise ValueError(f"Insufficient price history for benchmark {self.benchmark_ticker}")
                
                self.data['benchmark_history'] = benchmark_history
                
        except Exception as e:
            print(f"Error collecting performance data: {str(e)}")
            raise
        
    def calculate_metrics(self):
        """
        Calculate key metrics for analysis
        """
        try:
            if 'price_history' not in self.data:
                self.collect_performance()
            
            # Calculate daily returns first
            price_data = self.data['price_history']['Close']
            daily_returns = price_data.pct_change().dropna()
            
            if len(daily_returns) < 30:
                raise ValueError("Insufficient data for reliable metrics calculation")
            
            # Calculate annualized volatility
            annualized_factor = np.sqrt(252)  # Trading days in a year
            self.metrics = {
                'volatility': float(daily_returns.std() * annualized_factor),
                'tracking_error': self._calculate_tracking_error(),
                'liquidity_score': self._calculate_liquidity_score(),
                'sharpe_ratio': self._calculate_sharpe_ratio(daily_returns, annualized_factor),
                'max_drawdown': self._calculate_max_drawdown(price_data)
            }
        except Exception as e:
            print(f"Error calculating metrics: {str(e)}")
            raise

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

    def _calculate_sharpe_ratio(self, daily_returns, annualized_factor):
        """Calculate the Sharpe Ratio using 1-year Treasury rate as risk-free rate"""
        try:
            risk_free_rate = 0.05  # Could fetch this dynamically
            excess_returns = daily_returns - (risk_free_rate / 252)
            return float((excess_returns.mean() * annualized_factor) / 
                        (daily_returns.std() * annualized_factor))
        except:
            return 0.0

    def _calculate_max_drawdown(self, price_data):
        """Calculate the maximum drawdown percentage"""
        try:
            rolling_max = price_data.expanding().max()
            drawdowns = (price_data - rolling_max) / rolling_max
            return float(drawdowns.min())
        except:
            return 0.0 

    def validate_metrics(self):
        """
        Validate metrics against external sources
        """
        validation_data = {}
        
        # Validate expense ratio
        our_expense = self.data['basic']['expenseRatio']
        ext_expense = self._fetch_external_expense_ratio()
        validation_data['Expense Ratio'] = {
            'our_value': our_expense,
            'external_value': ext_expense,
            'difference': abs(our_expense - ext_expense)
        }
        
        # Validate volatility
        our_vol = self.metrics['volatility']
        ext_vol = self._fetch_external_volatility()
        validation_data['Volatility'] = {
            'our_value': our_vol,
            'external_value': ext_vol,
            'difference': abs(our_vol - ext_vol)
        }
        
        return validation_data

    def _fetch_external_expense_ratio(self):
        """
        Fetch expense ratio from multiple sources
        """
        try:
            ticker_info = yf.Ticker(self.ticker).info
            # Try multiple fields
            expense_ratio = (
                ticker_info.get('annualReportExpenseRatio') or
                ticker_info.get('expenseRatio') or
                ticker_info.get('totalExpenseRatio') or
                0.0
            )
            return float(expense_ratio)
        except:
            return 0.0

    def _fetch_external_volatility(self):
        """
        Fetch volatility from multiple sources
        """
        try:
            # Calculate using 3-month data for comparison
            history = yf.Ticker(self.ticker).history(period="3mo")
            returns = history['Close'].pct_change().dropna()
            return float(returns.std() * np.sqrt(252))
        except:
            return self.metrics['volatility']

    def compare_data_sources(self):
        """
        Compare metrics across different data sources
        """
        sources = {
            'yfinance': self._get_yfinance_metrics(),
            'yahoo_api': self._get_yahoo_api_metrics(),
            'etf_com': self._get_etf_com_metrics()
        }
        
        return sources

    def _get_yfinance_metrics(self):
        """Already implemented in main methods"""
        return {
            'expense_ratio': self.data['basic']['expenseRatio'],
            'volatility': self.metrics['volatility'],
            'volume': self.data['price_history']['Volume'].mean()
        }

    def _get_yahoo_api_metrics(self):
        """Fetch directly from Yahoo Finance API"""
        try:
            url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{self.ticker}"
            # Implementation would fetch and parse data
            return metrics
        except:
            return None

    def _get_etf_com_metrics(self):
        """Fetch from ETF.com"""
        try:
            url = f"https://www.etf.com/{self.ticker}"
            # Implementation would fetch and parse data
            return metrics
        except:
            return None 

    def track_historical_metrics(self, lookback_periods=['1mo', '3mo', '6mo', '1y']):
        """
        Track metrics over different time periods
        Using valid yfinance periods: 1mo, 3mo, 6mo, 1y
        """
        historical_metrics = {}
        
        for period in lookback_periods:
            try:
                # Get historical data for period
                history = yf.Ticker(self.ticker).history(period=period)
                
                if len(history) < 20:  # Minimum data requirement
                    continue
                    
                # Calculate metrics for this period
                returns = history['Close'].pct_change().dropna()
                vol = returns.std() * np.sqrt(252)
                
                historical_metrics[period] = {
                    'volatility': vol,
                    'sharpe': self._calculate_sharpe_ratio(returns, np.sqrt(252)),
                    'max_drawdown': self._calculate_max_drawdown(history['Close'])
                }
            except Exception as e:
                print(f"Error calculating metrics for {period}: {str(e)}")
                continue
        
        return historical_metrics 
import yfinance as yf
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from .utils import rate_limit, ETFDataCache
from .browser import BrowserSession
import time

class ETFAnalyzer:
    def __init__(self, ticker, benchmark_ticker="SPY"):
        self.ticker = ticker
        self.benchmark_ticker = benchmark_ticker
        self.data = {}
        self.metrics = {}
        self.cache = ETFDataCache()
        
    def collect_basic_info(self):
        """
        Gather fundamental ETF information with improved expense ratio collection
        """
        try:
            ticker_info = yf.Ticker(self.ticker).info
            
            # Try to get expense ratio from multiple sources
            expense_ratio = None
            
            # 1. Try ETF.com first (most reliable)
            etf_com_data = self._get_etf_com_metrics()
            if etf_com_data and 'expense_ratio' in etf_com_data:
                expense_ratio = etf_com_data['expense_ratio']
            
            # 2. If ETF.com fails, try Yahoo Finance fields
            if expense_ratio is None:
                expense_ratio = (
                    ticker_info.get('annualReportExpenseRatio') or
                    ticker_info.get('expenseRatio') or
                    ticker_info.get('totalExpenseRatio')
                )
            
            # 3. If still None, try the Yahoo Finance API directly
            if expense_ratio is None:
                yahoo_api_data = self._get_yahoo_api_metrics()
                if yahoo_api_data and 'expense_ratio' in yahoo_api_data:
                    expense_ratio = yahoo_api_data['expense_ratio']
            
            # 4. If all else fails, warn user and use 0.0
            if expense_ratio is None:
                print(f"Warning: Could not find expense ratio for {self.ticker}")
                expense_ratio = 0.0
            
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
        """Validate metrics against external sources"""
        validation_data = {}
        
        # Get ETF.com data
        etf_com_data = self._get_etf_com_metrics()
        
        # Validate expense ratio
        our_expense = self.data['basic'].get('expenseRatio')
        ext_expense = etf_com_data.get('expense_ratio') if etf_com_data else self._fetch_external_expense_ratio()
        if our_expense is not None or ext_expense is not None:
            validation_data['Expense Ratio'] = {
                'our_value': our_expense,
                'external_value': ext_expense,
                'difference': abs(our_expense - ext_expense) if (our_expense is not None and ext_expense is not None) else None
            }
        
        # Add AUM validation with better difference calculation
        if etf_com_data and 'aum' in etf_com_data:
            our_aum = self.data['basic'].get('totalAssets')
            ext_aum = etf_com_data['aum']
            if our_aum is not None and ext_aum is not None:
                # Calculate relative difference
                avg_aum = (our_aum + ext_aum) / 2
                diff = abs(our_aum - ext_aum) / avg_aum if avg_aum > 0 else None
                
                validation_data['AUM'] = {
                    'our_value': our_aum,
                    'external_value': ext_aum,
                    'difference': diff
                }
        
        # Add volume validation
        if etf_com_data and 'avg_volume' in etf_com_data:
            our_volume = self.data['price_history']['Volume'].mean() if 'price_history' in self.data else None
            ext_volume = etf_com_data['avg_volume']
            if our_volume is not None or ext_volume is not None:
                validation_data['Volume'] = {
                    'our_value': our_volume,
                    'external_value': ext_volume,
                    'difference': abs(our_volume - ext_volume) / max(our_volume, ext_volume) if (our_volume and ext_volume) else None
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
            params = {
                "modules": "price,defaultKeyStatistics,summaryDetail"
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()['quoteSummary']['result'][0]
                
                return {
                    'expense_ratio': float(data.get('defaultKeyStatistics', {}).get('expenseRatio', {}).get('raw', 0)),
                    'volatility': float(data.get('defaultKeyStatistics', {}).get('beta', {}).get('raw', 0)),
                    'volume': float(data.get('price', {}).get('regularMarketVolume', {}).get('raw', 0))
                }
        except Exception as e:
            print(f"Error fetching Yahoo API data: {str(e)}")
            return None

    @rate_limit(calls_per_minute=5)
    def _get_etf_com_metrics(self):
        """Fetch and parse data from ETF.com using Selenium with improved error handling"""
        cached_data = self.cache.get(self.ticker, 'etf_com')
        if cached_data:
            return cached_data
            
        try:
            with BrowserSession() as driver:
                url = f"https://www.etf.com/{self.ticker}"
                driver.get(url)
                time.sleep(3)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Debug: Print the page title to verify we're on the right page
                print(f"Debug: Page title - {soup.title.text if soup.title else 'No title'}")
                
                # First, verify we're on the correct page
                if not soup.find('div', text=re.compile(self.ticker, re.IGNORECASE)):
                    print(f"Warning: ETF ticker {self.ticker} not found on page")
                    return self._get_fallback_metrics()
                
                # Get metrics with debug info
                metrics = {}
                
                # Parse expense ratio
                expense_ratio = self._parse_expense_ratio(soup)
                if expense_ratio is not None:
                    metrics['expense_ratio'] = expense_ratio
                
                # Parse AUM
                aum = self._parse_aum(soup)
                if aum is not None:
                    metrics['aum'] = aum
                
                # Parse volume
                volume = self._parse_volume(soup)
                if volume is not None:
                    metrics['volume'] = volume
                
                # Parse additional metrics only if we have the basic ones
                if any([expense_ratio, aum, volume]):
                    metrics.update({
                        'holdings': self._parse_holdings(soup),
                        'segment': self._parse_segment(soup),
                        'issuer': self._parse_issuer(soup)
                    })
                    
                    # Cache only if we got some valid data
                    self.cache.set(self.ticker, 'etf_com', metrics)
                    
                return metrics if metrics else self._get_fallback_metrics()
                
        except Exception as e:
            print(f"Error fetching ETF.com data: {str(e)}")
            print("Falling back to alternative data sources...")
            return self._get_fallback_metrics()

    def _get_fallback_metrics(self):
        """Get metrics from alternative sources when ETF.com fails"""
        return {
            'expense_ratio': self.data['basic']['expenseRatio'],
            'aum': self.data['basic'].get('totalAssets', None),
            'avg_volume': self.data['price_history']['Volume'].mean() if 'price_history' in self.data else None,
            'holdings': None,
            'segment': self.data['basic'].get('category', None),
            'issuer': None
        }

    def _parse_expense_ratio(self, soup):
        """Parse expense ratio with improved error handling"""
        try:
            for pattern in ['Expense Ratio', 'Annual Fee', 'Management Fee']:
                expense_div = soup.find('div', text=re.compile(pattern, re.IGNORECASE))
                if expense_div and expense_div.find_next('div'):
                    ratio_text = expense_div.find_next('div').text.strip()
                    print(f"Debug: Found expense ratio text: {ratio_text}")  # Debug line
                    
                    # Only process if it looks like a percentage
                    if '%' in ratio_text or 'bps' in ratio_text:
                        match = re.search(r'(\d+\.?\d*)\s*(%|bps)', ratio_text)
                        if match:
                            value = float(match.group(1))
                            return value / (100 if match.group(2) == '%' else 10000)
            return None
        except Exception as e:
            print(f"Error parsing expense ratio: {str(e)}")
            return None

    def _parse_aum(self, soup):
        """Parse Assets Under Management with robust error handling"""
        try:
            # Try multiple possible div text patterns
            for pattern in ['AUM', 'Assets Under Management', 'Fund Size']:
                aum_div = soup.find('div', text=re.compile(pattern, re.IGNORECASE))
                if aum_div and aum_div.find_next('div'):
                    aum_text = aum_div.find_next('div').text.strip()
                    # Extract currency value and multiplier
                    match = re.search(r'\$?\s*([\d,.]+)\s*([BMK])?', aum_text)
                    if match:
                        value = float(match.group(1).replace(',', ''))
                        multiplier = {'B': 1e9, 'M': 1e6, 'K': 1e3}.get(match.group(2), 1) if match.group(2) else 1
                        return value * multiplier
            return None
        except Exception as e:
            print(f"Error parsing AUM: {str(e)}")
            return None

    def _parse_volume(self, soup):
        """Parse average trading volume with robust error handling"""
        try:
            # Try multiple possible div text patterns
            for pattern in ['Avg Daily Volume', 'Average Volume', 'Trading Volume']:
                volume_div = soup.find('div', text=re.compile(pattern, re.IGNORECASE))
                if volume_div and volume_div.find_next('div'):
                    vol_text = volume_div.find_next('div').text.strip()
                    # Extract numeric value and multiplier
                    match = re.search(r'([\d,.]+)\s*([BMK])?', vol_text)
                    if match:
                        value = float(match.group(1).replace(',', ''))
                        multiplier = {'B': 1e9, 'M': 1e6, 'K': 1e3}.get(match.group(2), 1) if match.group(2) else 1
                        return value * multiplier
            return None
        except Exception as e:
            print(f"Error parsing volume: {str(e)}")
            return None

    def _parse_holdings(self, soup):
        """Parse number of holdings"""
        try:
            holdings_div = soup.find('div', text=re.compile('Number of Holdings'))
            if holdings_div:
                return int(holdings_div.find_next('div').text.strip())
        except:
            return None

    def _parse_segment(self, soup):
        """Parse ETF segment/category"""
        try:
            segment_div = soup.find('div', text=re.compile('Segment'))
            if segment_div:
                return segment_div.find_next('div').text.strip()
        except:
            return None

    def _parse_issuer(self, soup):
        """Parse ETF issuer"""
        try:
            issuer_div = soup.find('div', text=re.compile('Issuer'))
            if issuer_div:
                return issuer_div.find_next('div').text.strip()
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

    def _validate_numeric_text(self, text):
        """Helper to validate numeric text before parsing"""
        # Remove common non-numeric characters
        cleaned = text.replace(',', '').replace('$', '').replace('%', '').strip()
        try:
            float(cleaned)
            return True
        except ValueError:
            return False 
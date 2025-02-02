import yfinance as yf
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from .utils import rate_limit, ETFDataCache
from .browser import BrowserSession
import time
from selenium.common.exceptions import WebDriverException
from requests.exceptions import RequestException
from datetime import datetime, time
import pytz

class MarketHoursError(Exception):
    """Raised when attempting real-time operations outside market hours"""
    pass

class ETFAnalyzer:
    # Add market hours constants
    MARKET_OPEN = time(9, 30)  # 9:30 AM ET
    MARKET_CLOSE = time(16, 0)  # 4:00 PM ET
    MARKET_TZ = pytz.timezone('America/New_York')
    
    def __init__(self, ticker, benchmark_ticker='SPY', debug=False):
        """
        Initialize ETF analyzer with optional custom benchmark
        
        Args:
            ticker (str): ETF ticker symbol
            benchmark (str): Benchmark ETF ticker (default: "SPY")
            debug (bool): Enable debug mode
        """
        self.ticker = ticker
        self.benchmark = benchmark_ticker
        self.debug = debug
        self.data = {'basic': {}, 'price_history': None}
        self.metrics = {}
        self.cache = ETFDataCache()
        self.browser = BrowserSession()
        
    def _debug(self, msg):
        if self.debug:
            print(f"Debug: {msg}")
        
    def collect_basic_info(self):
        """
        Gather fundamental ETF information with improved expense ratio collection
        """
        try:
            print("Debug: collect_basic_info started")  # Debug print
            ticker_info = yf.Ticker(self.ticker).info
            
            # Try to get expense ratio from multiple sources
            expense_ratio = None
            
            # 1. Try ETF.com first if Yahoo Finance doesn't have expense ratio
            if not any(ticker_info.get(field) for field in ['expenseRatio', 'annualReportExpenseRatio', 'totalExpenseRatio']):
                print("Debug: Attempting ETF.com lookup")  # Debug print
                try:
                    etf_com_data = self._get_etf_com_metrics()
                    if etf_com_data and 'expense_ratio' in etf_com_data:
                        expense_ratio = etf_com_data['expense_ratio']
                except WebDriverException as e:
                    print(f"Debug: WebDriverException caught: {str(e)}")  # Debug print
                    raise RuntimeError(f"Browser initialization failed: {str(e)}") from e
            
            # 2. If ETF.com fails or wasn't tried, use Yahoo Finance fields
            if expense_ratio is None:
                expense_ratio = (
                    ticker_info.get('annualReportExpenseRatio') or
                    ticker_info.get('expenseRatio') or
                    ticker_info.get('totalExpenseRatio')
                )
            
            # Store the basic info
            self.data['basic'] = {
                'name': ticker_info.get('longName', 'N/A'),
                'category': ticker_info.get('category', 'N/A'),
                'expenseRatio': float(expense_ratio) if expense_ratio is not None else 0.0,
                'totalAssets': ticker_info.get('totalAssets', 0.0),
                'description': ticker_info.get('description', 'N/A')
            }
            
        except RuntimeError:
            raise  # Re-raise RuntimeError without wrapping
        except Exception as e:
            print(f"Error collecting basic info for {self.ticker}: {str(e)}")
            raise RuntimeError(f"Failed to collect basic info: {str(e)}") from e
        
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
            print("Debug: collect_performance started")
            ticker_data = yf.Ticker(self.ticker)
            try:
                print("Debug: Attempting to get history")
                history = ticker_data.history(period="1y")
                print(f"Debug: Got {len(history)} days of history")
            except (RequestException, Exception) as e:
                print(f"Debug: Exception caught: {str(e)}")
                raise RuntimeError(f"Failed to fetch price history: {str(e)}") from e
            
            if len(history) < 30:
                raise ValueError(f"Insufficient price history for {self.ticker}")
            
            self.data['price_history'] = history
            
            # Get benchmark data if different
            if self.ticker != self.benchmark:
                try:
                    print("Debug: Getting benchmark history")
                    benchmark_data = yf.Ticker(self.benchmark)
                    self.data['benchmark_history'] = benchmark_data.history(period="1y")
                    print(f"Debug: Got {len(self.data['benchmark_history'])} days of benchmark history")
                except RequestException as e:
                    raise RuntimeError(f"Failed to fetch benchmark data: {str(e)}") from e
                
                if len(self.data['benchmark_history']) < 30:
                    raise ValueError(f"Insufficient price history for benchmark {self.benchmark}")
                
                # Ensure dates align
                common_dates = history.index.intersection(self.data['benchmark_history'].index)
                if len(common_dates) < 30:
                    raise ValueError("Insufficient overlapping data between ETF and benchmark")
                
                self.data['price_history'] = history.loc[common_dates]
                self.data['benchmark_history'] = self.data['benchmark_history'].loc[common_dates]
                print(f"Debug: Aligned {len(common_dates)} days of data")
            
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise  # Re-raise RuntimeError without wrapping
            raise RuntimeError(f"Failed to fetch price history: {str(e)}") from e
        
    def calculate_metrics(self):
        """
        Calculate key metrics for analysis
        """
        try:
            self.validate_data()  # Add validation before calculations
            
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
        """Calculate tracking error against custom benchmark"""
        try:
            if self.ticker == self.benchmark:
                print("Debug: Same ticker as benchmark, returning 0")
                return 0.0
            
            if 'benchmark_history' not in self.data:
                print("Debug: Getting benchmark history")
                benchmark_data = yf.Ticker(self.benchmark)
                benchmark_history = benchmark_data.history(period="1y")
                self.data['benchmark_history'] = benchmark_history
            
            # Calculate daily returns
            etf_returns = self.data['price_history']['Close'].pct_change().dropna()
            benchmark_returns = self.data['benchmark_history']['Close'].pct_change().dropna()
            
            print(f"Debug: ETF returns mean: {etf_returns.mean():.4f}")
            print(f"Debug: Benchmark returns mean: {benchmark_returns.mean():.4f}")
            
            # Align the dates
            etf_returns, benchmark_returns = etf_returns.align(benchmark_returns, join='inner')
            
            print(f"Debug: Number of aligned returns: {len(etf_returns)}")
            
            if len(etf_returns) == 0 or len(benchmark_returns) == 0:
                print("Debug: No aligned returns, returning 0")
                return 0.0
            
            # Calculate tracking error
            return_differences = etf_returns - benchmark_returns
            tracking_error = return_differences.std() * np.sqrt(252)  # Annualized
            
            print(f"Debug: Return differences std: {return_differences.std():.4f}")
            print(f"Debug: Tracking error: {tracking_error:.4f}")
            
            return float(tracking_error)
        except Exception as e:
            print(f"Error calculating tracking error: {str(e)}")
            return 0.0
        
    def _calculate_liquidity_score(self):
        """Calculate detailed liquidity score"""
        try:
            # Initialize scores
            self.metrics['volume_score'] = 0.0
            self.metrics['spread_score'] = 0.0
            self.metrics['asset_score'] = 0.0
            
            # Volume score (40% weight)
            volume = self.data['price_history']['Volume'].mean()
            self.metrics['volume_score'] = min(40, volume / 25000)  # 1M volume = 40 points
            
            # Spread score (30% weight)
            spread = self.data.get('real_time', {}).get('spread_pct', 0.01)
            self.metrics['spread_score'] = min(30, (0.01 / spread) * 30)  # 0.01% spread = 30 points
            
            # Asset score (30% weight)
            aum = self.data['basic'].get('totalAssets', 0)
            self.metrics['asset_score'] = min(30, (aum / 1e9) * 30)  # $1B AUM = 30 points
            
            # Total score
            return self.metrics['volume_score'] + self.metrics['spread_score'] + self.metrics['asset_score']
        except Exception as e:
            print(f"Error calculating liquidity score: {str(e)}")
            # Initialize scores on error
            self.metrics['volume_score'] = 0.0
            self.metrics['spread_score'] = 0.0
            self.metrics['asset_score'] = 0.0
            return 0.0

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
        """Get ETF metrics from ETF.com"""
        try:
            # Get the ETF.com page
            url = f"https://www.etf.com/{self.ticker}"
            self.browser.get(url)
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            
            # First, verify we're on the correct page
            if not soup.find('div', string=re.compile(self.ticker, re.IGNORECASE)):  # Changed text to string
                print(f"Warning: ETF ticker {self.ticker} not found on page")
                return self._get_fallback_metrics()
            
            # Parse metrics
            metrics = {}
            metrics['expense_ratio'] = self._parse_expense_ratio(soup)
            metrics['aum'] = self._parse_aum(soup)
            metrics['volume'] = self._parse_volume(soup)
            metrics['spread'] = self._parse_spread(soup)
            
            return metrics
            
        except WebDriverException as e:
            print(f"Error fetching ETF.com data: {e}")
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
                expense_div = soup.find('div', string=re.compile(pattern, re.IGNORECASE))  # Changed text to string
                if expense_div and expense_div.find_next('div'):
                    ratio_text = expense_div.find_next('div').text.strip()
                    # Only process if it looks like a percentage
                    if '%' in ratio_text or 'bps' in ratio_text:
                        match = re.search(r'(\d+\.?\d*)\s*(%|bps)', ratio_text)
                        if match:
                            value = float(match.group(1))
                            return value / (100 if match.group(2) == '%' else 10000)
        except Exception as e:
            print(f"Error parsing expense ratio: {e}")
        return None

    def _parse_aum(self, soup):
        """Parse Assets Under Management with robust error handling"""
        try:
            for pattern in ['AUM', 'Assets Under Management', 'Fund Size']:
                aum_div = soup.find('div', string=re.compile(pattern, re.IGNORECASE))  # Changed text to string
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
            for pattern in ['Avg Daily Volume', 'Average Volume', 'Trading Volume']:
                volume_div = soup.find('div', string=re.compile(pattern, re.IGNORECASE))  # Changed text to string
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

    def collect_real_time_data(self):
        """Collect real-time trading data with market hours handling"""
        try:
            if not self._is_market_open():
                # Get last known values if market is closed
                rt_data = self._get_last_known_values()
                rt_data['market_status'] = 'closed'
                self.data['real_time'] = rt_data
                return rt_data
            
            # Market is open, get real-time data
            ticker_data = yf.Ticker(self.ticker)
            quote = ticker_data.info
            
            rt_data = {
                'bid': quote.get('bid'),
                'ask': quote.get('ask'),
                'last_price': quote.get('regularMarketPrice'),
                'iiv': None,  # Always include IIV field, even if None
                'timestamp': quote.get('regularMarketTime'),
                'market_status': 'open'
            }
            
            # Calculate spread if we have valid bid/ask
            if all(isinstance(rt_data[x], (int, float)) for x in ['bid', 'ask']):
                if rt_data['bid'] > 0 and rt_data['ask'] > 0:
                    rt_data['spread'] = rt_data['ask'] - rt_data['bid']
                    rt_data['spread_pct'] = rt_data['spread'] / ((rt_data['bid'] + rt_data['ask']) / 2)
            
            self.data['real_time'] = rt_data
            return rt_data
            
        except Exception as e:
            print(f"Error collecting real-time data: {str(e)}")
            return self._get_last_known_values()
    
    def _get_last_known_values(self):
        """Get last known trading values when market is closed"""
        try:
            history = yf.Ticker(self.ticker).history(period='1d')
            if len(history) > 0:
                last_row = history.iloc[-1]
                return {
                    'bid': None,
                    'ask': None,
                    'last_price': last_row['Close'],
                    'timestamp': last_row.name,
                    'market_status': 'closed'
                }
        except Exception as e:
            print(f"Error getting last known values: {str(e)}")
        return None

    def analyze_market_making(self):
        """Analyze market maker effectiveness and liquidity provision"""
        try:
            # Get intraday data (1-minute intervals)
            intraday = yf.download(self.ticker, period="1d", interval="1m")
            
            # Market maker metrics
            metrics = {
                'quote_presence': 0,  # % of time with valid quotes
                'spread_stability': 0,  # How stable is the spread
                'depth_score': 0,     # Estimate of market depth
                'price_continuity': 0  # Smoothness of price changes
            }
            
            if len(intraday) > 0:
                # Calculate quote presence
                valid_quotes = ((intraday['Bid'] > 0) & (intraday['Ask'] > 0)).mean()
                metrics['quote_presence'] = float(valid_quotes)
                
                # Calculate spread stability
                spreads = intraday['Ask'] - intraday['Bid']
                metrics['spread_stability'] = 1 - float(spreads.std() / spreads.mean())
                
                # Estimate market depth using volume and price impact
                avg_trade_size = intraday['Volume'].mean()
                price_impact = abs(intraday['High'] - intraday['Low']).mean()
                metrics['depth_score'] = float(avg_trade_size / (price_impact + 0.00001))
                
                # Calculate price continuity
                price_changes = intraday['Close'].pct_change().dropna()
                metrics['price_continuity'] = 1 - float(abs(price_changes).mean())
                
                # Add additional analysis
                metrics.update({
                    'avg_trade_size': avg_trade_size,
                    'price_impact': price_impact,
                    'quote_count': len(intraday),
                    'spread_percentiles': {
                        '25': float(spreads.quantile(0.25)),
                        '50': float(spreads.quantile(0.50)),
                        '75': float(spreads.quantile(0.75))
                    }
                })
                
            return metrics
        except Exception as e:
            print(f"Error analyzing market making: {str(e)}")
            return None 

    def analyze_trading_costs(self):
        """Analyze total trading costs including spread, impact, and fees"""
        try:
            # Initialize with default values if 'basic' doesn't exist
            expense_ratio = self.data.get('basic', {}).get('expenseRatio', 0.0)
            costs = {
                'explicit': {'expense_ratio': expense_ratio},
                'implicit': {'spread_cost': None, 'market_impact': None},
                'total': {'one_way': expense_ratio, 'round_trip': expense_ratio * 2},
                'alerts': []
            }

            # Get real-time data
            rt_data = self.data.get('real_time', {})
            
            # Check if we have any real-time data
            if not rt_data:
                costs['alerts'].append("No real-time data available - showing expense ratio only")
                return costs

            # Check if we have valid bid/ask
            bid = rt_data.get('bid')
            ask = rt_data.get('ask')
            if not bid or not ask or bid <= 0 or ask <= 0:
                costs['alerts'].append("No real-time bid/ask data available")
                return costs

            # Calculate spread cost
            spread_pct = (ask - bid) / ((bid + ask) / 2)
            costs['implicit']['spread_cost'] = spread_pct / 2
            
            # Calculate market impact if we have volume data
            avg_volume = self.data.get('price_history', {}).get('Volume', pd.Series()).mean()
            if avg_volume and avg_volume > 0:
                impact_factor = 0.1  # 10% of spread for normal size trades
                costs['implicit']['market_impact'] = costs['implicit']['spread_cost'] * impact_factor
            else:
                # No volume data available - use default impact
                costs['implicit']['market_impact'] = costs['implicit']['spread_cost'] * 0.1
                costs['alerts'].append("Using default market impact estimate - no volume data available")
            
            # Calculate total costs
            spread_cost = costs['implicit']['spread_cost'] or 0.0
            market_impact = costs['implicit']['market_impact'] or 0.0
            costs['total']['one_way'] = spread_cost + market_impact + expense_ratio
            costs['total']['round_trip'] = (spread_cost + market_impact + expense_ratio) * 2

            return costs

        except Exception as e:
            print(f"Error analyzing trading costs: {str(e)}")
            return {
                'explicit': {'expense_ratio': expense_ratio},
                'implicit': {'spread_cost': None, 'market_impact': None},
                'total': {'one_way': expense_ratio, 'round_trip': expense_ratio * 2},
                'alerts': [f"Error calculating costs: {str(e)}"]
            }

    def analyze_premium_discount(self):
        """Analyze premium/discount to NAV and set alerts"""
        try:
            rt_data = self.data.get('real_time', {})
            if not rt_data or not rt_data.get('iiv'):
                return None
            
            analysis = {
                'current': {},
                'historical': {},
                'alerts': []
            }
            
            # Current premium/discount
            last_price = rt_data.get('last_price')
            iiv = rt_data.get('iiv')
            if last_price and iiv:
                premium_discount = ((last_price - iiv) / iiv) * 100
                analysis['current'] = {
                    'premium_discount': premium_discount,
                    'last_price': last_price,
                    'iiv': iiv
                }
                
                # Set alerts based on thresholds
                if abs(premium_discount) > 0.5:  # 0.5% threshold
                    analysis['alerts'].append(
                        f"Large premium/discount: {premium_discount:+.2f}% "
                        f"({'premium' if premium_discount > 0 else 'discount'})"
                    )
                
                return analysis
            return None
        except Exception as e:
            print(f"Error analyzing premium/discount: {str(e)}")
            return None 

    def validate_data(self):
        """Validate data consistency"""
        if 'price_history' not in self.data:
            raise ValueError("Missing price history data")
        
        required_columns = ['Close', 'High', 'Low', 'Volume']
        if not all(col in self.data['price_history'].columns for col in required_columns):
            raise ValueError("Missing required columns in price history")
        
        # Check for empty data
        if len(self.data['price_history']) == 0:
            raise ValueError("Insufficient data")
        
        # Check for invalid values and NaN/None
        df = self.data['price_history']
        for col in required_columns:
            if df[col].isna().any():
                raise ValueError("Inconsistent data lengths")
            try:
                df[col].astype(float)
            except ValueError:
                raise ValueError("Invalid price data - non-numeric values found")
        
        # Check data consistency - compare with index length
        index_length = len(df.index)
        for col in required_columns:
            if len(df[col].dropna()) != index_length:
                raise ValueError("Inconsistent data lengths")
        
        # Check dates - handle both DatetimeIndex and RangeIndex
        now = pd.Timestamp.now(tz='UTC')
        index_dates = self.data['price_history'].index
        if hasattr(index_dates, 'tz'):  # Only check timezone if it's a DatetimeIndex
            if index_dates.tz is None:
                index_dates = index_dates.tz_localize('UTC')
            elif index_dates.tz != now.tz:
                index_dates = index_dates.tz_convert('UTC')
            
            if any(date > now for date in index_dates):
                raise ValueError("Invalid dates - future dates found in price history") 

    def validate_real_time_data(self):
        """Validate real-time data"""
        if 'real_time' not in self.data:
            raise ValueError("No real-time data available")
        
        rt_data = self.data['real_time']
        
        # Check bid/ask validity
        if rt_data.get('bid') and rt_data.get('ask'):
            if rt_data['bid'] >= rt_data['ask']:
                raise ValueError("Invalid bid/ask prices - bid must be less than ask")
            
        # Check timestamp freshness
        if rt_data.get('timestamp'):
            now = pd.Timestamp.now(tz='UTC')
            timestamp = pd.Timestamp(rt_data['timestamp'])
            if timestamp.tz is None:
                timestamp = timestamp.tz_localize('UTC')
            age = now - timestamp
            if age > pd.Timedelta(minutes=15):
                raise ValueError("Stale data - real-time data is more than 15 minutes old") 

    def _parse_spread(self, soup):
        """Parse bid-ask spread with robust error handling"""
        try:
            for pattern in ['Spread', 'Bid-Ask Spread']:
                spread_div = soup.find('div', string=re.compile(pattern, re.IGNORECASE))
                if spread_div and spread_div.find_next('div'):
                    spread_text = spread_div.find_next('div').text.strip()
                    if '%' in spread_text:
                        match = re.search(r'(\d+\.?\d*)\s*%', spread_text)
                        if match:
                            return float(match.group(1)) / 100
            return None
        except Exception as e:
            print(f"Error parsing spread: {str(e)}")
            return None 

    def _is_market_open(self):
        """Check if the US market is currently open"""
        now = datetime.now(self.MARKET_TZ)
        current_time = now.time()
        
        # Check if it's a weekday (0 = Monday, 4 = Friday)
        if now.weekday() > 4:
            return False
            
        # Check if within market hours
        return self.MARKET_OPEN <= current_time <= self.MARKET_CLOSE 
import time
from functools import wraps
from datetime import datetime, timedelta
import json
import os

def rate_limit(calls_per_minute=10):
    """Rate limiting decorator"""
    intervals = {}  # Store last call time for each function
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = datetime.now()
            func_name = func.__name__
            
            if func_name in intervals:
                last_call = intervals[func_name]
                min_interval = timedelta(minutes=1) / calls_per_minute
                
                if now - last_call < min_interval:
                    sleep_time = (min_interval - (now - last_call)).total_seconds()
                    time.sleep(sleep_time)
            
            intervals[func_name] = now
            return func(*args, **kwargs)
        return wrapper
    return decorator

class ETFDataCache:
    """Cache for ETF data"""
    def __init__(self, cache_dir='.cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get(self, ticker, source):
        """Get cached data if it exists and is fresh"""
        cache_file = os.path.join(self.cache_dir, f"{ticker}_{source}.json")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
                
            # Check if cache is less than 24 hours old
            if datetime.now().timestamp() - cached_data['timestamp'] < 86400:
                return cached_data['data']
        return None
    
    def set(self, ticker, source, data):
        """Cache data with timestamp"""
        cache_file = os.path.join(self.cache_dir, f"{ticker}_{source}.json")
        
        cache_data = {
            'timestamp': datetime.now().timestamp(),
            'data': data
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f) 
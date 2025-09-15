"""
Data fetching module for truly autonomous AI trading agent
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from typing import Dict, List, Optional
import time

class DataFetcher:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Autonomous AI Agent/1.0'})
        
    def get_stock_fundamentals(self, symbol: str) -> Dict:
        """
        Get fundamental data for a stock using multiple fallback sources
        """
        try:
            # Try yfinance first as primary source
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return {}
            
            return {
                'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'sector': info.get('sector', 'Unknown'),
                'company_name': info.get('longName', symbol),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', np.nan),
                'beta': info.get('beta', 1.0),
                'employees': info.get('fullTimeEmployees', 0),
                'exchange': info.get('exchange', ''),
                'dividend_yield': info.get('dividendYield', np.nan)
            }
        except Exception as e:
            print(f"Error fetching fundamentals for {symbol}: {e}")
            return {}
    
    def get_historical_data(self, symbol: str, period: str = '6mo') -> pd.DataFrame:
        """
        Get historical price data using yfinance as primary source
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            return hist
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_news_sentiment(self, symbol: str) -> Dict:
        """
        Get news sentiment for a stock from Finnhub
        """
        try:
            url = f"{self.config.DATA_SOURCES['finnhub_base']}/news-sentiment?symbol={symbol}&token={self.config.FINNHUB_API_KEY}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data if isinstance(data, dict) else {}
            else:
                return {}
        except Exception as e:
            print(f"Error fetching news sentiment for {symbol}: {e}")
            return {}
    
    def get_company_news(self, symbol: str, days: int = 30) -> List[Dict]:
        """
        Get recent company news from Finnhub
        """
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            url = f"{self.config.DATA_SOURCES['finnhub_base']}/company-news?symbol={symbol}&from={start_date}&to={end_date}&token={self.config.FINNHUB_API_KEY}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data if isinstance(data, list) else []
            else:
                return []
        except Exception as e:
            print(f"Error fetching company news for {symbol}: {e}")
            return []

# Example usage
if __name__ == "__main__":
    pass
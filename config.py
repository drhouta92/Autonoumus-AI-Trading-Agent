"""
Configuration settings for truly autonomous AI trading agent
"""

# API Keys
FINNHUB_API_KEY = "xxxxx"
ALPHA_VANTAGE_API_KEY = "xxxxxxx"
POLYGON_API_KEY = "xxxxxxxx"

# Data Sources
DATA_SOURCES = {
    'premarket_data': 'https://financialmodelingprep.com/api/v3/stock_market/premarket',
    'earnings_calendar': 'https://financialmodelingprep.com/api/v3/earning_calendar',
    'news_sentiment': 'https://finnhub.io/api/v1/news-sentiment',
    'technical_indicators': 'https://www.alphavantage.co/query',
    'polygon_base': 'https://api.polygon.io/v2',
    'finnhub_base': 'https://finnhub.io/api/v1',
    'financialmodelingprep_base': 'https://financialmodelingprep.com/api/v3'
}

# Analysis Parameters
CONFIDENCE_THRESHOLD = 0.7
VOLUME_SPIKE_THRESHOLD = 2.0
PRICE_CHANGE_THRESHOLD = 2.0
RSI_OVERBOUGHT = 75
RSI_OVERSOLD = 25

# Risk Management
MAX_POSITION_SIZE = 0.02
MAX_PORTFOLIO_RISK = 0.01
STOP_LOSS_PERCENT = 0.30
TAKE_PROFIT_PERCENT = 1.0

# Technical Analysis Parameters
MOVING_AVERAGES = [10, 20, 50]
INDICATORS = ['RSI', 'MACD', 'BBANDS', 'STOCH']

# Penny Stock Parameters
PENNY_STOCK_MAX_PRICE = 15.0
PENNY_STOCK_MIN_PRICE = 0.5
MIN_VOLUME_FOR_PENNY = 50000

# Trading Hours
MARKET_OPEN = "09:30"
MARKET_CLOSE = "16:00"
PREMARKET_START = "04:00"
PREMARKET_END = "09:30"
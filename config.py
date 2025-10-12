"""
Configuration settings for Micro-Cap AI Agent 2.5
Preserves existing API keys and data sources
Adds micro-cap specific parameters
"""

# API Keys (PRESERVED)
FINNHUB_API_KEY = "xxxxx"
ALPHA_VANTAGE_API_KEY = "xxxxxxx"
POLYGON_API_KEY = "xxxxxxxx"

# Data Sources (PRESERVED)
DATA_SOURCES = {
    'premarket_data': 'https://financialmodelingprep.com/api/v3/stock_market/premarket',
    'earnings_calendar': 'https://financialmodelingprep.com/api/v3/earning_calendar',
    'news_sentiment': 'https://finnhub.io/api/v1/news-sentiment',
    'technical_indicators': 'https://www.alphavantage.co/query',
    'polygon_base': 'https://api.polygon.io/v2',
    'finnhub_base': 'https://finnhub.io/api/v1',
    'financialmodelingprep_base': 'https://financialmodelingprep.com/api/v3'
}

# Micro-Cap Specific Parameters
MICRO_CAP_MAX_MARKET_CAP = 300_000_000    # $300M
MICRO_CAP_MIN_MARKET_CAP = 5_000_000      # $5M
NANO_CAP_THRESHOLD = 50_000_000           # $50M (extra caution)

# Penny Stock Parameters (UPDATED for micro-caps)
PENNY_STOCK_MAX_PRICE = 5.0               # NYSE/NASDAQ definition
PENNY_STOCK_MIN_PRICE = 0.10              # Minimum to avoid sub-penny
MIN_VOLUME_FOR_PENNY = 50_000
MIN_AVG_VOLUME_MICROCAP = 100_000         # Higher liquidity requirement

# Risk Management (UPDATED for micro-caps)
MAX_POSITION_SIZE = 0.02                  # 2% max per position
PENNY_MAX_POSITION_SIZE = 0.01            # 1% max for penny stocks
MAX_PORTFOLIO_RISK = 0.05                 # 5% total risk (higher for micro-caps)
STOP_LOSS_PERCENT = 0.15                  # 15% stop for micro-caps
PENNY_STOP_LOSS_PERCENT = 0.25            # 25% stop for penny stocks
TAKE_PROFIT_PERCENT = 0.45                # 45% target for micro-caps
PENNY_TAKE_PROFIT_PERCENT = 0.75          # 75% target for penny stocks
MIN_RISK_REWARD_RATIO = 2.0               # Minimum 2:1 R:R

# Liquidity Requirements
MIN_LIQUIDITY_RATIO = 0.01                # Position < 1% of daily volume
PREFERRED_LIQUIDITY_RATIO = 0.005         # Preferred < 0.5% of daily volume

# Technical Analysis Parameters
MOVING_AVERAGES = [10, 20, 50]
INDICATORS = ['RSI', 'MACD', 'BBANDS', 'STOCH', 'ADX', 'ATR']
MIN_DATA_POINTS = 20                      # Reduced for micro-caps

# Analysis Thresholds (UPDATED)
CONFIDENCE_THRESHOLD = 0.65               # Slightly lower for micro-caps
VOLUME_SPIKE_THRESHOLD = 2.0
PRICE_CHANGE_THRESHOLD = 2.0
RSI_OVERBOUGHT = 75
RSI_OVERSOLD = 25
MIN_OVERALL_SCORE = 0.55                  # Minimum score to consider

# Brain Evolution Parameters
BRAIN_PERFORMANCE_THRESHOLD = 0.5         # Kill-gate threshold
BRAIN_ZOMBIE_GRACE_PERIOD = 5             # Generations before kill
BRAIN_AUTO_SAVE_INTERVAL = 300            # 5 minutes
BRAIN_MAX_JSON_GENERATIONS = 100          # Rotate to SQLite after this

# Learning Parameters
LEARNING_RATE = 0.1
MIN_LEARNING_SAMPLES = 10
LEARNING_HISTORY_DAYS = 30

# Persistence Settings
JSON_RETENTION_DAYS = 7                   # Keep JSON for 7 days
AUTO_MIGRATION_ENABLED = True             # Auto-migrate old data to SQLite

# Trading Hours (PRESERVED)
MARKET_OPEN = "09:30"
MARKET_CLOSE = "16:00"
PREMARKET_START = "04:00"
PREMARKET_END = "09:30"

# Agent Tree Weights (Default, adjusted by brain)
SCORING_WEIGHTS = {
    'technical': 0.30,
    'momentum': 0.25,
    'catalyst': 0.20,
    'risk_adjusted': 0.15,
    'liquidity': 0.10
}

DISCOVERY_WEIGHTS = {
    'indices': 1.0,
    'etfs': 1.0,
    'news': 1.2,
    'sectors': 1.0,
    'trending': 1.3,
    'websites': 1.1,
    'micro_cap_screeners': 1.5,
    'penny_stock_sources': 1.4
}
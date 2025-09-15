Truly Autonomous AI Trading Agent with Learning
This project is an advanced AI agent designed to autonomously discover, analyze, and rank stock trading opportunities. Unlike traditional systems that rely on static watchlists, this agent builds its own universe of stocks from scratch, learns from historical performance, and adapts its strategy over time.

Key Features
Autonomous Discovery: The agent builds its stock universe by scraping major indices, ETFs, news sites, and trending tickers. It uses a weighted system for discovery methods that is updated based on historical performance.

Multi-Factor Analysis: Each discovered stock is analyzed based on a composite score that considers multiple factors, including:

Catalyst Detection: The CatalystDetector module analyzes news sentiment and detects volume anomalies to identify potential market catalysts.

Technical Analysis: The system analyzes various technical indicators like RSI, MACD, and moving averages.

Fundamental Data: It fetches key fundamental data such as P/E ratio, Beta, and market capitalization.

Adaptive Learning: The agent incorporates two learning mechanisms to improve its performance:

Stock Learner: A component that remembers past discoveries and learns from their performance over time by adjusting scoring weights.

Reinforcement Learning: A Q-learning model that learns to rank opportunities and adjusts the agent's confidence threshold based on the success or failure of previous trades.

Robust Data Fetching: The DataFetcher module aggregates data from multiple APIs, including Finnhub, Alpha Vantage, Polygon, and yfinance, with built-in fallbacks.

Comprehensive Risk Management: The RiskManager module calculates appropriate position sizes, stop-loss, and take-profit levels using configurable methods like fixed fractional or volatility-adjusted approaches.

How It Works
The agent follows a systematic, automated workflow:

Initialize Components: The main.py script initializes all modules, including DataFetcher, TechnicalAnalyzer, CatalystDetector, RiskManager, and AutonomousDiscovery.

Discover Stock Universe: The AutonomousDiscovery module builds a fresh list of symbols to analyze, incorporating learning from previously discovered stocks saved in historical_stocks.json and stock_performance.json.

Analyze Opportunities: The agent iterates through the discovered symbols, fetching data and calculating an overall score for each based on momentum, catalysts, and other factors.

Rank and Select: The ReinforcementLearner module uses its Q-table to rank the analyzed opportunities, providing a final, learned recommendation.

Output Analysis: The main.py script then presents a summary of the best opportunities by category, such as highest score, best momentum, and best catalysts.

Quick Start Guide
Prerequisites
Python 3.x

Required libraries (see requirements.txt which would be included in the project): pandas, numpy, yfinance, requests, bs4, joblib.

API keys for Finnhub, Alpha Vantage, and Polygon (configured in config.py).

Installation and Usage
Clone the repository.

Install dependencies: pip install -r requirements.txt

Add your API keys to config.py.

Run the main script from your terminal: python main.py

The agent will begin its autonomous discovery and analysis process, with results printed to the console.

File Structure
main.py: The main entry point for the application.

autonomous_discovery.py: Handles the discovery and generation of the stock universe.

data_fetcher.py: Manages all data retrieval from various APIs.

catalyst_detector.py: Focuses on analyzing news sentiment and volume anomalies.

technical_analyzer.py: Analyzes technical indicators and patterns.

stock_learner.py: Implements a learning mechanism that adjusts scoring weights based on historical performance.

reinforcement_learner.py: Implements a Q-learning model for ranking opportunities and adapting the overall strategy.

risk_manager.py: Contains logic for calculating position sizes and managing risk.

config.py: Configuration file for API keys and analysis parameters.

historical_stocks.json: Stores a history of discovered symbols.

stock_performance.json: Stores performance data for discovered stocks.

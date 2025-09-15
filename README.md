

# 🧠 Truly Autonomous AI Trading Agent with Learning

An advanced **AI-driven trading agent** that autonomously discovers, analyzes, and ranks stock opportunities. Unlike traditional systems that depend on static watchlists, this agent dynamically builds its own universe of stocks, **learns from historical outcomes**, and continuously adapts its strategy with **reinforcement learning**.

---

## ✨ Key Features

### 🚀 Autonomous Discovery

* Builds a **dynamic stock universe** from scratch.
* Sources symbols from indices, ETFs, trending tickers, and financial news.
* Uses a **weighted discovery system**, updated based on past performance.

### 📊 Multi-Factor Analysis

Each discovered stock is scored using a **composite ranking system**:

* **Catalyst Detection** → Sentiment analysis + volume anomaly detection.
* **Technical Analysis** → Indicators like RSI, MACD, SMA/EMA crossovers.
* **Fundamental Data** → Ratios, beta, and market cap integration.

### 🧩 Adaptive Learning

* **Stock Learner** → Remembers past stock outcomes, dynamically adjusts scoring weights.
* **Reinforcement Learner (Q-Learning)** → Learns to rank trade opportunities, adapts confidence thresholds based on trade success/failure.

### 🔗 Robust Data Fetching

* Aggregates from **Finnhub, Alpha Vantage, Polygon, yfinance**.
* Built-in **failover** mechanisms to ensure uninterrupted data flow.

### 🛡 Comprehensive Risk Management

* Calculates **position sizes, stop-loss, and take-profit** levels.
* Supports both **fixed fractional** and **volatility-adjusted** methods.

---

## ⚙️ How It Works

1. **Initialize Components** → Launches all modules (`DataFetcher`, `CatalystDetector`, `TechnicalAnalyzer`, etc.).
2. **Discover Stock Universe** → Fresh symbols generated + historical learning applied.
3. **Analyze Opportunities** → Multi-factor scoring across momentum, catalysts, fundamentals.
4. **Rank & Select** → Q-learning ranks opportunities with dynamic thresholds.
5. **Output Analysis** → Returns top-ranked stocks with categories (highest score, best momentum, strongest catalysts).

---

## 🛠 Quick Start

### Prerequisites

* Python **3.x**
* API keys for: **Finnhub, Alpha Vantage, Polygon**

### Installation

```bash
# Clone the repository
git clone https://github.com/drhouta92/autonomous-trading-agent.git
cd autonomous-trading-agent

# Install dependencies
pip install -r requirements.txt

# Add your API keys
nano config.py
```

### Usage

```bash
python main.py
```

Results will be displayed in the console, grouped by **category and ranking**.

---

## 📂 File Structure

```
├── main.py                  # Main entry point
├── autonomous_discovery.py  # Stock discovery engine
├── data_fetcher.py          # Data retrieval + API integrations
├── catalyst_detector.py     # Sentiment + volume anomaly detection
├── technical_analyzer.py    # Technical indicators analysis
├── stock_learner.py         # Adaptive learning for scoring
├── reinforcement_learner.py # Q-learning ranking system
├── risk_manager.py          # Position sizing & risk control
├── config.py                # API keys & parameters
├── historical_stocks.json   # Persistent stock universe
├── stock_performance.json   # Past performance database
└── requirements.txt         # Python dependencies
```

---

## 📈 Example Output

```
📊 Top Opportunities:

1️⃣ Highest Score → AAPL (Momentum + Catalyst Alignment)
2️⃣ Best Momentum → TSLA (Strong RSI + EMA Crossover)
3️⃣ Strongest Catalyst → NVDA (News Sentiment Surge + Volume Spike)
```

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss your ideas.

---

## ⚠️ Disclaimer

This project is for **educational and research purposes only**.
It is **not financial advice**. Use at your own risk.


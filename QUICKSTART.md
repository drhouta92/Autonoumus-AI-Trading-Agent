# Micro-Cap AI Agent 2.5 - Quick Start Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- API keys for data sources (optional for initial testing)

### Installation

```bash
# Clone the repository
git clone https://github.com/drhouta92/Autonoumus-AI-Trading-Agent.git
cd Autonoumus-AI-Trading-Agent

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Edit `config.py` with your API keys (optional for testing):

```python
FINNHUB_API_KEY = "your_key_here"
ALPHA_VANTAGE_API_KEY = "your_key_here"
POLYGON_API_KEY = "your_key_here"
```

### Run the Agent

```bash
python main.py
```

## 📊 What Happens When You Run It

### Phase 1: Discovery (30-60 seconds)
```
🔍 Discovering micro-cap stocks...
- Scanning small-cap ETFs
- Scraping penny stock screeners
- Mining micro-cap news
- Detecting volume spikes
✅ Discovered 150 symbols
```

### Phase 2: Filtering (20-40 seconds)
```
🔍 Filtering for micro-cap criteria...
- Market cap: $5M - $300M
- Liquidity: >100K avg volume
- Price: >$0.10
✅ Qualified 45 micro-caps
```

### Phase 3: Analysis (2-5 minutes)
```
📊 Analyzing top 20 opportunities...
[1/20] MICR... ✅
[2/20] TINY... ✅
...
✅ Analyzed 18 opportunities
```

### Phase 4: Decisions (5-10 seconds)
```
🎯 Making trading decisions...
✅ BUY signals: 3
   Top confidence: 78.5%
```

### Phase 5: Results
```
TOP MICRO-CAP OPPORTUNITIES
═══════════════════════════
1. MICR
   Price: $2.450
   Market Cap: $85,000,000
   Overall Score: 0.785
   Technical Score: 0.812
   Risk Level: moderate
   Suggested Position: 200 shares
   Stop Loss: $1.838
   Take Profit: $3.553
   Risk/Reward: 2.81:1
   💎 MICRO-CAP
```

## 🧠 Brain Evolution

The agent learns over time through kill-gate evolution:

### Generation 0 (First Run)
```
Brain Generation: 0
Brain Status: alive
Performance: N/A (first run)
```

### After Multiple Runs
```
Brain Generation: 12
Brain Status: alive
Current Performance: 68.5%
Avg Performance: 62.3%
Total Archived: 8
```

### If Performance Drops
```
⚠️ Brain marked as ZOMBIE (performance: 0.42)
⚠️ Brain still ZOMBIE (2/5)
💀 Brain KILLED after 5 zombie generations
🔄 Brain REBORN as generation 13
```

## 📁 Generated Files

### After First Run
```
brain_state.json              # Current brain generation
brain_history.db              # Historical brain states
data/
  ├── json/
  │   ├── opportunities_20251012.json
  │   └── decisions_20251012.json
  └── trading.db              # Main database
microcap_ai_agent_report_20251012_143022.csv
```

## 🎛️ Key Configuration Options

### Adjust Risk (config.py)
```python
MAX_POSITION_SIZE = 0.02           # 2% per position
PENNY_MAX_POSITION_SIZE = 0.01     # 1% for penny stocks
MAX_PORTFOLIO_RISK = 0.05          # 5% total risk
```

### Adjust Market Cap Range
```python
MICRO_CAP_MAX_MARKET_CAP = 300_000_000  # $300M
MICRO_CAP_MIN_MARKET_CAP = 5_000_000    # $5M
```

### Adjust Penny Stock Definition
```python
PENNY_STOCK_MAX_PRICE = 5.0      # $5.00
PENNY_STOCK_MIN_PRICE = 0.10     # $0.10
```

### Adjust Confidence Threshold
```python
CONFIDENCE_THRESHOLD = 0.65      # Minimum to consider
MIN_OVERALL_SCORE = 0.55         # Minimum overall score
```

## 🔧 Advanced Usage

### Run Specific Phases

```python
from agent_orchestrator import AgentOrchestrator
import config

orchestrator = AgentOrchestrator(config)

# Run only discovery
opportunities = orchestrator.run_discovery_cycle()

# Run only analysis
analyzed = orchestrator.run_analysis_cycle(opportunities[:10])

# Run only decisions
decisions = orchestrator.run_decision_cycle(analyzed)
```

### Access Brain Directly

```python
from brain_manager import BrainManager
import config

brain = BrainManager(config)

# Get statistics
stats = brain.get_brain_statistics()
print(f"Generation: {stats['current_generation']}")
print(f"Status: {stats['current_status']}")

# Record decision
brain.record_decision('MICR', 'BUY', 0.85)

# Evolve brain
performance = 0.65
learning_data = {'weight_adjustments': {'momentum': 0.05}}
brain.evolve_brain(performance, learning_data)
```

### Query Database

```python
import sqlite3

conn = sqlite3.connect('data/trading.db')
cursor = conn.cursor()

# Get all opportunities
cursor.execute('SELECT * FROM opportunities ORDER BY overall_score DESC LIMIT 10')
for row in cursor.fetchall():
    print(row)

# Get buy decisions
cursor.execute('SELECT * FROM decisions WHERE action = "BUY"')
for row in cursor.fetchall():
    print(row)

conn.close()
```

### Export Data

```python
from persistence_manager import PersistenceManager
import config

pm = PersistenceManager(config)

# Export everything to CSV
pm.export_to_csv('exports')

# Get statistics
stats = pm.get_statistics()
print(f"Total opportunities: {stats['total_opportunities']}")
print(f"Total decisions: {stats['total_decisions']}")
```

## 📈 Understanding Scores

### Overall Score (0-1)
Composite score from:
- Technical Analysis: 30%
- Momentum: 25%
- Catalyst/News: 20%
- Risk-Adjusted: 15%
- Liquidity: 10%

### Technical Score (0-1)
Based on:
- RSI oversold/bullish signals
- MACD crossovers
- Stochastic signals
- Bullish patterns
- Volume analysis

### Risk Level (1-5)
1. Low risk
2. Low-moderate risk
3. Moderate risk (acceptable)
4. High risk (caution)
5. Extreme risk (avoid)

## 🛡️ Risk Management

### Automatic Position Sizing
The agent calculates:
- Maximum shares based on portfolio risk
- Liquidity-adjusted position size
- Volatility-adjusted stops

### Example Position Calculation
```
Entry Price: $2.50
Portfolio Value: $100,000
Max Risk: 2% = $2,000
Stop Loss: 15% = $2.125
Risk per share: $0.375
Position Size: $2,000 / $0.375 = 5,333 shares

BUT adjusted for liquidity:
Daily Volume: 250,000
Max 1% of volume: 2,500 shares
Final Position: 2,500 shares
```

## 🔄 Learning Cycle

The agent learns from:
1. **Sector Performance**: Which sectors produce best opportunities
2. **Pattern Success**: Which technical patterns work best
3. **Timing**: Optimal times for finding opportunities
4. **Confidence Calibration**: How accurate confidence scores are

Learning applies to:
- Discovery weights (where to look)
- Scoring weights (what matters most)
- Threshold adjustments (when to act)

## ⚠️ Important Notes

### This is Educational Software
- Not financial advice
- For research and learning only
- Use at your own risk

### API Rate Limits
- Free APIs have rate limits
- Agent includes delays to respect limits
- Consider paid tiers for production use

### Data Quality
- Discovery depends on web scraping (can break)
- Some sources may be unavailable
- Agent continues with available data

### Backtesting
- No backtesting engine included
- Focus on discovery and analysis
- Paper trade before live trading

## 🐛 Troubleshooting

### "No opportunities discovered"
- Check internet connection
- Verify web scraping still works
- Increase discovery time
- Lower filters temporarily

### "Module not found"
```bash
pip install -r requirements.txt
```

### "API error"
- Check API keys in config.py
- Verify API key validity
- Check rate limits

### "Insufficient data"
- Stock may be too new
- Try different symbols
- Lower MIN_DATA_POINTS in config

## 📚 Learn More

- See `ARCHITECTURE.md` for detailed system design
- See `README.md` for project overview
- See inline code comments for implementation details

## 🤝 Contributing

Pull requests welcome! Focus on:
- Additional data sources
- Better filtering logic
- Improved pattern detection
- Risk management enhancements

## 📄 License

See LICENSE file in repository.

---

**Happy Trading! 🚀**
Remember: This is an AI agent for discovery and analysis, not a guaranteed profit machine. Always do your own due diligence!

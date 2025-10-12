# Micro-Cap AI Agent 2.5 Architecture

## Overview
Complete autonomous trading agent specialized for micro-cap and penny stocks with kill-gate brain evolution system.

## Agent Tree Structure

```
┌─────────────────────────────────────┐
│      Agent Orchestrator             │
│   (Coordinates all branches)        │
└─────────────────┬───────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
    ┌───▼────┐         ┌───▼────┐
    │ Brain  │         │Persist │
    │Manager │         │Manager │
    └───┬────┘         └───┬────┘
        │                  │
        │              ┌───▼────────┐
        │              │  Offline   │
        │              │  Learner   │
        │              └────────────┘
        │
    ┌───▼──────────────────────────────┐
    │      7 Core Processing Branches  │
    └──────────────────────────────────┘
            │
    ┌───────┴──────┬──────────┬─────────┬──────────┬──────────┬─────────┐
    │              │          │         │          │          │         │
┌───▼────┐   ┌────▼───┐ ┌────▼───┐ ┌──▼────┐ ┌──▼────┐ ┌────▼───┐ ┌──▼─────┐
│Discovery│   │ Fetch  │ │Technical│ │Catalyst│ │  Risk │ │Decision│ │Learning│
│ Branch  │   │ Branch │ │Analysis │ │Detector│ │Manager│ │ Engine │ │ Branch │
└─────────┘   └────────┘ └─────────┘ └────────┘ └───────┘ └────────┘ └────────┘
```

## Core Modules (12 Files)

### 1. Brain Manager (`brain_manager.py`)
**Purpose**: Central intelligence with kill-gate evolution
- Single-file JSON state for fast access
- Auto-rotation to SQLite for historical data
- Hot-switch capability between JSON and SQLite
- Kill-gate evolution mechanism:
  - **Alive**: Performing above threshold
  - **Zombie**: Underperforming but given grace period
  - **Killed**: Terminated and reborn with mutated parameters
- Offline learning integration
- Auto-save with background threading

**Key Features**:
- Generation tracking
- Performance scoring
- Learned patterns storage
- Decision history
- Dynamic weight adjustments

### 2. Micro-Cap Discovery (`micro_cap_discovery.py`)
**Discovery Branch**: Specialized micro-cap and penny stock discovery
- Scans small-cap ETF holdings
- Scrapes penny stock screeners
- Mines micro-cap news sources
- Scans OTC/Pink Sheet markets
- Detects unusual volume spikes
- Filters by market cap ($5M - $300M)
- Identifies penny stocks (< $5.00)
- Ensures liquidity (>100K avg volume)

**Filtering Criteria**:
- Market cap range
- Price range
- Volume requirements
- Exchange listing
- Liquidity scoring

### 3. Advanced Technical Analyzer (`advanced_technical_analyzer.py`)
**Analysis Branch**: Specialized for micro-cap volatility
- RSI, MACD, Bollinger Bands, Stochastic
- ADX (trend strength), ATR (volatility)
- Candlestick pattern detection
- Chart pattern recognition (breakouts, consolidation)
- Momentum classification
- Support/Resistance levels
- Volume analysis with OBV
- Technical score calculation (0-1)

**Micro-Cap Adaptations**:
- Reduced minimum data points (20 vs 50)
- Volatility-adjusted indicators
- High volatility pattern recognition

### 4. Micro-Cap Risk Manager (`micro_cap_risk_manager.py`)
**Risk Branch**: Specialized risk management
- Position sizing based on:
  - Portfolio percentage (1-2% max)
  - Liquidity constraints
  - Volatility adjustment
- Dynamic stop losses (ATR-based)
- Trailing stops for profit protection
- Risk assessment scoring (1-5 scale)
- Kelly Criterion for optimal sizing
- Portfolio heat monitoring

**Risk Factors**:
- Market cap (nano-cap extreme risk)
- Price (penny stock risk)
- Liquidity (volume-based)
- Volatility (historical vol)
- Beta (market correlation)

### 5. Decision Engine (`decision_engine.py`)
**Decision Branch**: Final decision making
- Integrates all analysis components
- Weighted scoring system:
  - Technical: 30%
  - Momentum: 25%
  - Catalyst: 20%
  - Risk-adjusted: 15%
  - Liquidity: 10%
- Brain-based adjustments
- Confidence thresholds
- Action determination (BUY/SELL/HOLD/PASS)
- Batch decision processing
- Human-readable explanations

### 6. Persistence Manager (`persistence_manager.py`)
**Persistence Branch**: Dual storage system
- JSON for recent/fast access (7 days)
- SQLite for historical data
- Auto-migration of old data
- Tables:
  - opportunities
  - decisions
  - positions
  - performance
- Export to CSV capability
- Statistics tracking

### 7. Offline Learner (`offline_learner.py`)
**Learning Branch**: Continuous improvement
- Sector performance analysis
- Pattern success tracking
- Timing optimization
- Confidence calibration
- Weight adjustment recommendations
- Win rate estimation
- Learning report generation

**Learning Insights**:
- Top performing sectors
- Successful patterns
- Optimal entry times
- Confidence accuracy
- Overall performance metrics

### 8. Agent Orchestrator (`agent_orchestrator.py`)
**Main Coordinator**: Executes complete cycles
- Phase 1: Discovery
- Phase 2: Filtering
- Phase 3: Opportunity ranking
- Phase 4: Deep analysis
- Phase 5: Decision making
- Phase 6: Persistence
- Phase 7: Offline learning
- Graceful shutdown handling

### 9. Data Fetcher (`data_fetcher.py`)
**Fetch Branch**: Multi-source data retrieval (PRESERVED)
- yfinance for historical data
- Finnhub API integration
- Alpha Vantage support
- Polygon API support
- Fundamentals data
- News sentiment
- Company news

### 10. Catalyst Detector (`catalyst_detector.py`)
**Analysis Branch**: News and sentiment (PRESERVED)
- News sentiment scoring
- Buzz score calculation
- Volume anomaly detection
- Earnings calendar
- News scraping

### 11. Config (`config.py`)
**Configuration**: All parameters in one place
- API keys (PRESERVED)
- Data sources (PRESERVED)
- Micro-cap parameters (ADDED)
- Risk management settings (UPDATED)
- Brain evolution settings (ADDED)
- Learning parameters (ADDED)
- Scoring weights (ADDED)

### 12. Utilities (`utils.py`)
**Supporting Functions**: Common utilities
- Currency formatting
- Percentage formatting
- Market hours checking
- Returns calculation
- Sharpe ratio, max drawdown
- Symbol validation
- Safe file operations
- Data manipulation helpers

## File Naming Convention
All files use **snake_case** naming:
- `brain_manager.py`
- `micro_cap_discovery.py`
- `advanced_technical_analyzer.py`
- `micro_cap_risk_manager.py`
- `decision_engine.py`
- `persistence_manager.py`
- `offline_learner.py`
- `agent_orchestrator.py`
- `utils.py`

Class names match file names where logical:
- `BrainManager` in `brain_manager.py`
- `MicroCapDiscovery` in `micro_cap_discovery.py`
- `AdvancedTechnicalAnalyzer` in `advanced_technical_analyzer.py`

## Kill-Gate Brain Evolution

### States
1. **Alive**: Performance ≥ threshold (0.5)
2. **Zombie**: Performance < threshold, grace period active
3. **Killed**: Terminated after zombie grace period (5 generations)

### Evolution Process
1. Evaluate performance score
2. Compare to threshold
3. Update status (alive/zombie/killed)
4. If zombie for too long → kill and rebirth
5. Mutate weights (±30%) on rebirth
6. Apply learning adjustments
7. Archive to database
8. Save current state to JSON

### Brain Storage
- **JSON** (`brain_state.json`): Current generation, fast access
- **SQLite** (`brain_history.db`): All historical generations
- **Auto-rotation**: After 100 generations
- **Hot-switch**: Instant migration to SQLite-only mode

## Data Flow

```
1. Discovery → Symbols discovered from multiple sources
2. Filtering → Apply micro-cap criteria
3. Ranking → Score by opportunity potential
4. Fetch → Get historical data for top candidates
5. Technical Analysis → Calculate indicators and patterns
6. Catalyst Detection → Analyze news and sentiment
7. Risk Assessment → Evaluate risk factors
8. Position Sizing → Calculate optimal position
9. Decision Making → Integrate all scores
10. Persistence → Save to JSON/SQLite
11. Learning → Extract insights
12. Brain Evolution → Update weights and generation
```

## Running the Agent

```bash
python main.py
```

This executes one complete cycle through all branches.

## Configuration

Edit `config.py` to adjust:
- API keys
- Market cap ranges
- Risk parameters
- Scoring weights
- Learning parameters

## Persistence

### JSON Files (Recent Data)
- `data/json/opportunities_YYYYMMDD.json`
- `data/json/decisions_YYYYMMDD.json`

### SQLite Database (Historical)
- `data/trading.db`
  - opportunities table
  - decisions table
  - positions table
  - performance table

### Brain State
- `brain_state.json` - Current generation
- `brain_history.db` - All generations

## Learning Cycle

Every run:
1. Load historical data (30 days)
2. Analyze sector performance
3. Track pattern success
4. Calibrate confidence
5. Generate weight adjustments
6. Update brain with insights
7. Evolve or maintain generation

## API Keys Required

Edit `config.py`:
- `FINNHUB_API_KEY` - For news and sentiment
- `ALPHA_VANTAGE_API_KEY` - For technical indicators
- `POLYGON_API_KEY` - For market data

## Libraries Used (Preserved)

All existing libraries maintained:
- pandas, numpy - Data analysis
- yfinance - Market data
- talib - Technical indicators
- requests, beautifulsoup4 - Web scraping
- scikit-learn, joblib - Machine learning
- sqlite3 (built-in) - Database

## Micro-Cap Focus

Specialized for:
- Market cap: $5M - $300M
- Penny stocks: $0.10 - $5.00
- High volatility handling
- Liquidity requirements
- OTC market support
- Risk-adjusted positioning

## Output

- Console: Real-time progress and results
- CSV: Full analysis report with timestamp
- JSON: Opportunities and decisions
- SQLite: Historical database
- Brain: Evolution state tracking

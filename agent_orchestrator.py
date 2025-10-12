"""
Agent Orchestrator
Coordinates all agent modules in tree structure:
- Discovery Branch
- Fetch Branch
- Analysis Branch
- Decision Branch
- Persistence Branch
- Learning Branch
"""

import time
from typing import Dict, List, Optional
from datetime import datetime
import yfinance as yf

# Import all modules
from brain_manager import BrainManager
from micro_cap_discovery import MicroCapDiscovery
from data_fetcher import DataFetcher
from advanced_technical_analyzer import AdvancedTechnicalAnalyzer
from catalyst_detector import CatalystDetector
from micro_cap_risk_manager import MicroCapRiskManager
from decision_engine import DecisionEngine
from persistence_manager import PersistenceManager
from offline_learner import OfflineLearner

class AgentOrchestrator:
    """
    Main orchestrator for Micro-Cap AI Agent 2.5
    Manages agent tree with 7 core branches
    """
    
    def __init__(self, config):
        self.config = config
        print("🚀 Initializing Micro-Cap AI Agent 2.5...")
        print("=" * 60)
        
        # Initialize core brain
        print("🧠 Initializing Brain Manager (Kill-Gate Evolution)...")
        self.brain = BrainManager(config)
        
        # Initialize persistence layer
        print("💾 Initializing Persistence Manager...")
        self.persistence = PersistenceManager(config)
        
        # Initialize offline learner
        print("📚 Initializing Offline Learner...")
        self.learner = OfflineLearner(config, self.persistence)
        
        # Initialize discovery branch
        print("🔍 Initializing Discovery Branch...")
        self.discovery = MicroCapDiscovery(config, self.brain)
        
        # Initialize fetch branch
        print("📡 Initializing Data Fetch Branch...")
        self.data_fetcher = DataFetcher(config)
        
        # Initialize analysis branches
        print("📊 Initializing Analysis Branches...")
        self.technical_analyzer = AdvancedTechnicalAnalyzer(config)
        self.catalyst_detector = CatalystDetector(config, self.data_fetcher)
        self.risk_manager = MicroCapRiskManager(config)
        
        # Initialize decision branch
        print("🎯 Initializing Decision Engine...")
        self.decision_engine = DecisionEngine(config, self.brain)
        
        print("=" * 60)
        print("✅ All modules initialized successfully!")
        print()
        
        # Start brain auto-save
        self.brain.start_auto_save()
    
    def run_discovery_cycle(self) -> List[Dict]:
        """
        Execute full discovery cycle
        Discovery Branch → Fetch Branch → Analysis Branches
        """
        print("\n" + "=" * 60)
        print("DISCOVERY CYCLE - Micro-Cap AI Agent 2.5")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Brain Generation: {self.brain.generation}")
        print(f"Brain Status: {self.brain.current_brain.kill_gate_status}")
        print()
        
        # Phase 1: Discovery
        print("PHASE 1: DISCOVERY")
        print("-" * 60)
        discovered_symbols = self.discovery.discover_micro_caps()
        print(f"✅ Discovered {len(discovered_symbols)} symbols")
        print()
        
        # Phase 2: Filtering
        print("PHASE 2: FILTERING")
        print("-" * 60)
        filtered_stocks = self.discovery.filter_micro_caps(discovered_symbols)
        print(f"✅ Filtered to {len(filtered_stocks)} qualified micro-caps")
        print()
        
        # Phase 3: Ranking
        print("PHASE 3: OPPORTUNITY RANKING")
        print("-" * 60)
        ranked_stocks = self.discovery.rank_by_opportunity(filtered_stocks)
        print(f"✅ Ranked all opportunities")
        print()
        
        return ranked_stocks
    
    def run_analysis_cycle(self, opportunities: List[Dict]) -> List[Dict]:
        """
        Execute analysis cycle on opportunities
        Analysis Branches (Technical, Catalyst, Risk)
        """
        print("PHASE 4: DEEP ANALYSIS")
        print("-" * 60)
        print(f"Analyzing {len(opportunities)} opportunities...")
        
        analyzed_opportunities = []
        
        for i, opp in enumerate(opportunities, 1):
            symbol = opp['symbol']
            print(f"  [{i}/{len(opportunities)}] Analyzing {symbol}...", end=" ")
            
            try:
                # Fetch historical data
                ticker = yf.Ticker(symbol)
                hist_data = ticker.history(period='3mo')
                
                if hist_data.empty or len(hist_data) < 20:
                    print("❌ Insufficient data")
                    continue
                
                # Technical analysis
                technical_analysis = self.technical_analyzer.analyze_micro_cap(
                    hist_data, symbol
                )
                
                # Catalyst detection
                catalyst_data = self.catalyst_detector.detect_catalysts(symbol)
                
                # Risk assessment
                risk_assessment = self.risk_manager.assess_micro_cap_risk(
                    symbol=symbol,
                    market_cap=opp['market_cap'],
                    price=opp['price'],
                    avg_volume=opp['avg_volume'],
                    volatility=technical_analysis.get('volatility', {}).get('historical_vol', 0.5),
                    beta=1.0
                )
                
                # Position calculation
                position = self.risk_manager.calculate_position(
                    symbol=symbol,
                    entry_price=opp['price'],
                    market_cap=opp['market_cap'],
                    avg_volume=opp['avg_volume'],
                    volatility=technical_analysis.get('volatility', {}).get('historical_vol', 0.5),
                    is_penny=opp['is_penny_stock']
                )
                
                # Compile analysis
                full_analysis = {
                    'symbol': symbol,
                    'fundamentals': opp,
                    'technical': technical_analysis,
                    'catalyst': catalyst_data,
                    'risk': risk_assessment,
                    'position': position,
                    'momentum': technical_analysis.get('momentum', {}),
                    'overall_score': self._calculate_composite_score(
                        technical_analysis, catalyst_data, risk_assessment
                    )
                }
                
                analyzed_opportunities.append(full_analysis)
                print("✅")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}")
                continue
        
        print(f"✅ Analyzed {len(analyzed_opportunities)} opportunities")
        print()
        
        return analyzed_opportunities
    
    def run_decision_cycle(self, analyzed_opportunities: List[Dict]) -> List:
        """
        Execute decision cycle
        Decision Branch
        """
        print("PHASE 5: DECISION MAKING")
        print("-" * 60)
        
        decisions = self.decision_engine.batch_decisions(analyzed_opportunities)
        
        # Filter for actionable decisions
        buy_decisions = self.decision_engine.filter_decisions(decisions, "BUY")
        
        print(f"✅ Made {len(decisions)} decisions")
        print(f"   BUY signals: {len(buy_decisions)}")
        print(f"   Top confidence: {buy_decisions[0].confidence:.1%}" if buy_decisions else "   No buy signals")
        print()
        
        return buy_decisions
    
    def run_persistence_cycle(self, opportunities: List[Dict], 
                             decisions: List) -> None:
        """
        Execute persistence cycle
        Persistence Branch
        """
        print("PHASE 6: PERSISTENCE")
        print("-" * 60)
        
        # Save opportunities
        for opp in opportunities:
            self.persistence.save_opportunity(opp, use_json=True)
        
        # Save decisions
        for decision in decisions:
            self.persistence.save_decision(decision, use_json=True)
        
        # Check if migration needed
        stats = self.persistence.get_statistics()
        if stats['json_files'] > 30:
            print("  Migrating old data to SQLite...")
            self.persistence.migrate_to_sqlite(days_to_keep_json=7)
        
        print(f"✅ Persisted {len(opportunities)} opportunities and {len(decisions)} decisions")
        print()
    
    def run_learning_cycle(self) -> Dict:
        """
        Execute learning cycle
        Learning Branch
        """
        print("PHASE 7: OFFLINE LEARNING")
        print("-" * 60)
        
        # Learn from history
        insights = self.learner.learn_from_history(days=30)
        
        # Apply learning to brain
        if insights:
            performance_score = insights.get('overall_performance', {}).get('estimated_win_rate', 0.5)
            learning_data = {
                'successful_sectors': insights.get('sector_analysis', {}).get('top_sectors', []),
                'successful_patterns': insights.get('pattern_analysis', {}).get('successful_patterns', []),
                'weight_adjustments': insights.get('weight_adjustments', {})
            }
            
            # Evolve brain
            self.brain.evolve_brain(performance_score, learning_data)
            
            print(f"✅ Learning complete. Performance score: {performance_score:.1%}")
            print(f"   Brain generation: {self.brain.generation}")
            print(f"   Brain status: {self.brain.current_brain.kill_gate_status}")
        else:
            print("⚠️  Insufficient data for learning")
        
        print()
        
        return insights
    
    def _calculate_composite_score(self, technical: Dict, catalyst: Dict, 
                                   risk: Dict) -> float:
        """Calculate composite opportunity score"""
        weights = {
            'technical': 0.40,
            'catalyst': 0.30,
            'risk': 0.30
        }
        
        tech_score = technical.get('technical_score', 0.0)
        
        # Catalyst score from sentiment and buzz
        catalyst_score = (
            (catalyst.get('sentiment_score', 0.0) + 1) / 2 * 0.5 +
            catalyst.get('buzz_score', 0.0) * 0.5
        )
        
        # Risk score (invert so lower risk = higher score)
        risk_level = risk.get('risk_level', 3)
        risk_score = (6 - risk_level) / 5.0
        
        composite = (
            tech_score * weights['technical'] +
            catalyst_score * weights['catalyst'] +
            risk_score * weights['risk']
        )
        
        return min(composite, 1.0)
    
    def run_full_cycle(self) -> Dict:
        """
        Execute complete agent cycle through all branches
        """
        start_time = time.time()
        
        # Discovery cycle
        opportunities = self.run_discovery_cycle()
        
        if not opportunities:
            print("⚠️  No opportunities discovered. Ending cycle.")
            return {}
        
        # Analysis cycle (top 20 for performance)
        top_opportunities = opportunities[:20]
        analyzed = self.run_analysis_cycle(top_opportunities)
        
        if not analyzed:
            print("⚠️  No opportunities passed analysis. Ending cycle.")
            return {}
        
        # Decision cycle
        decisions = self.run_decision_cycle(analyzed)
        
        # Persistence cycle
        self.run_persistence_cycle(analyzed, decisions)
        
        # Learning cycle
        insights = self.run_learning_cycle()
        
        # Summary
        elapsed = time.time() - start_time
        
        print("=" * 60)
        print("CYCLE COMPLETE")
        print("=" * 60)
        print(f"Duration: {elapsed:.1f} seconds")
        print(f"Opportunities discovered: {len(opportunities)}")
        print(f"Opportunities analyzed: {len(analyzed)}")
        print(f"Buy decisions: {len([d for d in decisions if d.action == 'BUY'])}")
        print(f"Brain generation: {self.brain.generation}")
        print("=" * 60)
        print()
        
        return {
            'opportunities': opportunities,
            'analyzed': analyzed,
            'decisions': decisions,
            'insights': insights,
            'brain_stats': self.brain.get_brain_statistics()
        }
    
    def shutdown(self):
        """Graceful shutdown"""
        print("\n🛑 Shutting down Micro-Cap AI Agent 2.5...")
        self.brain.stop_auto_save()
        self.brain._save_brain()
        print("✅ Shutdown complete")

# Example usage
if __name__ == "__main__":
    import config
    
    orchestrator = AgentOrchestrator(config)
    
    try:
        results = orchestrator.run_full_cycle()
        
        # Display top decisions
        if results.get('decisions'):
            print("\n📊 TOP DECISIONS:")
            print("-" * 60)
            for i, decision in enumerate(results['decisions'][:5], 1):
                print(f"{i}. {decision.symbol} - {decision.action} ({decision.confidence:.1%})")
    
    finally:
        orchestrator.shutdown()

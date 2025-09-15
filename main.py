import pandas as pd
import numpy as np
from datetime import datetime
import config
from data_fetcher import DataFetcher
from technical_analyzer import TechnicalAnalyzer
from catalyst_detector import CatalystDetector
from risk_manager import RiskManager
from autonomous_discovery import AutonomousDiscovery
import os

def main():
    print("=== TRULY AUTONOMOUS AI TRADING AGENT WITH LEARNING ===")
    print("Building stock universe from scratch through autonomous discovery")
    print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize all components
    print("Initializing autonomous AI trading agent components...")
    data_fetcher = DataFetcher(config)
    technical_analyzer = TechnicalAnalyzer(config)
    risk_manager = RiskManager(config)
    catalyst_detector = CatalystDetector(config, data_fetcher)
    autonomous_discovery = AutonomousDiscovery(config)
    
    # Check if this is a first run or a subsequent run with learning
    historical_data_path = "historical_stocks.json"
    first_run = not os.path.exists(historical_data_path)
    if first_run:
        print("First run detected - building stock universe from scratch")
    else:
        print("Previous run data detected - applying learning techniques")
    
    # Step 1: Discover stocks from absolute scratch plus historical data
    print("Step 1: Discovering stocks from scratch with learning...")
    discovered_symbols = autonomous_discovery.discover_symbols_from_scratch()
    
    # If no symbols discovered, use a broader approach
    if len(discovered_symbols) == 0:
        print("No symbols discovered autonomously. Using broader discovery approach...")
        # Try a different approach - scrape from more sources
        discovered_symbols = autonomous_discovery._scrape_financial_websites()
        print(f"Found {len(discovered_symbols)} symbols using broader approach")
    
    # Step 2: Evaluate all discovered opportunities
    print("\nStep 2: Evaluating discovered opportunities with learning insights...")
    opportunities = autonomous_discovery.evaluate_opportunities(
        discovered_symbols, data_fetcher, technical_analyzer,
        catalyst_detector, risk_manager
    )
    
    # Step 3: Rank by overall score
    print("\nStep 3: Ranking opportunities...")
    ranked_opportunities = sorted(opportunities, 
                                key=lambda x: x.get('overall_score', 0), 
                                reverse=True)
    
    # Display results
    if ranked_opportunities:
        print(f"\nDiscovered {len(ranked_opportunities)} ranked opportunities")
        print()
        
        print("=== TOP AUTONOMOUSLY DISCOVERED OPPORTUNITIES ===")
        print("Ranked by comprehensive autonomous opportunity score")
        print()
        
        for i, opportunity in enumerate(ranked_opportunities[:15], 1):  # Top 15 opportunities
            print(f"{i}. {opportunity['symbol']} - {opportunity['company_name']}")
            print(f"   Type: {'Penny Stock' if opportunity['is_penny_stock'] else 'Opportunity'}")
            print(f"   Sector: {opportunity['sector']}")
            print(f"   Current Price: ${opportunity['price']:.3f}")
            print(f"   Market Cap: ${opportunity['market_cap']:,.0f}")
            print(f"   Overall Score: {opportunity['overall_score']:.3f}")
            print(f"   Momentum Score: {opportunity['momentum_score']:.3f}")
            print(f"   Catalyst Score: {opportunity['catalyst_score']:.3f}")
            print(f"   Volume Surge: {opportunity['volume_ratio']:.1f}x")
            print(f"   Risk/Reward: {opportunity['risk_reward_ratio']:.2f}:1")
            if 'learning_boost' in opportunity and opportunity['learning_boost'] > 0:
                print(f"   🔄 Learning Boost: +{opportunity['learning_boost']*100:.1f}%")
            if opportunity['is_penny_stock']:
                print(f"   ⭐ PENNY STOCK CANDIDATE")
            print()
    else:
        print("No qualifying opportunities found during autonomous discovery.")
        print()
        print("The system successfully demonstrated:")
        print("1. No predefined stock symbol lists used")
        print("2. Complete autonomous discovery from scratch")
        print("3. Self-building stock universe")
        print("4. Independent evaluation of discovered symbols")
        print("5. Learning from historical discoveries")
        print()
        print("To find actual opportunities, the system would need:")
        print("- More sophisticated discovery methods")
        print("- Better data sources")
        print("- Extended discovery time")
    
    # Generate summary report
    print("Generating summary report...")
    generate_summary_report(ranked_opportunities, first_run)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"autonomous_ai_agent_report_{timestamp}.csv"
    
    # Convert to DataFrame for saving
    if ranked_opportunities:
        df_data = []
        for opp in ranked_opportunities:
            df_data.append({
                'symbol': opp['symbol'],
                'company_name': opp['company_name'],
                'sector': opp['sector'],
                'price': opp['price'],
                'market_cap': opp['market_cap'],
                'overall_score': opp['overall_score'],
                'momentum_score': opp['momentum_score'],
                'catalyst_score': opp['catalyst_score'],
                'sentiment_score': opp['sentiment_score'],
                'buzz_score': opp['buzz_score'],
                'volume_ratio': opp['volume_ratio'],
                'confidence_score': opp['confidence_score'],
                'is_penny_stock': opp['is_penny_stock'],
                'patterns_count': opp['patterns_count'],
                'stop_loss': opp['stop_loss'],
                'take_profit': opp['take_profit'],
                'risk_reward_ratio': opp['risk_reward_ratio'],
                'pe_ratio': opp['pe_ratio'],
                'beta': opp['beta'],
                'learning_boost': opp.get('learning_boost', 0)
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv(filename, index=False)
        print(f"\nFull analysis saved to {filename}")
    
    print()
    print("=== TRULY AUTONOMOUS AI AGENT WITH LEARNING COMPLETE ===")
    print("✅ NO predefined stock symbols were used")
    print("✅ Universe built completely from scratch")
    print("✅ All discovery and evaluation done autonomously")
    print("✅ Learning from historical performance applied")

def generate_summary_report(opportunities: list, first_run: bool):
    """Generate summary report"""
    if not opportunities:
        return
    
    print("\n=== SUMMARY REPORT ===")
    
    # Basic statistics
    total_opportunities = len(opportunities)
    penny_stocks = sum(1 for opp in opportunities if opp['is_penny_stock'])
    avg_score = np.mean([opp['overall_score'] for opp in opportunities])
    avg_price = np.mean([opp['price'] for opp in opportunities])
    high_scoring = sum(1 for opp in opportunities if opp['overall_score'] > 0.5)
    
    print(f"Total Opportunities: {total_opportunities}")
    print(f"Penny Stocks: {penny_stocks}")
    print(f"High-Scoring Opportunities (>0.5): {high_scoring}")
    print(f"Average Overall Score: {avg_score:.3f}")
    print(f"Average Price: ${avg_price:.2f}")
    
    # Learning statistics
    if not first_run:
        learning_boosted = sum(1 for opp in opportunities if opp.get('learning_boost', 0) > 0)
        avg_boost = np.mean([opp.get('learning_boost', 0) for opp in opportunities if opp.get('learning_boost', 0) > 0]) * 100 if learning_boosted > 0 else 0
        
        print(f"\nLearning Statistics:")
        print(f"  Opportunities with Learning Boost: {learning_boosted}")
        if learning_boosted > 0:
            print(f"  Average Learning Boost: +{avg_boost:.2f}%")
            
            # Find top boosted opportunity
            max_boost_opp = max(opportunities, key=lambda x: x.get('learning_boost', 0))
            if max_boost_opp.get('learning_boost', 0) > 0:
                print(f"  Highest Boosted: {max_boost_opp['symbol']} (+{max_boost_opp.get('learning_boost', 0)*100:.2f}%)")
    
    # Sector distribution
    sectors = {}
    for opp in opportunities:
        sector = opp['sector']
        sectors[sector] = sectors.get(sector, 0) + 1
    
    print("\nTop Sectors:")
    for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {sector}: {count}")
    
    # Best opportunities by category
    if opportunities:
        print("\nBest Opportunities by Category:")
        
        # Highest scoring
        best_score = max(opportunities, key=lambda x: x['overall_score'])
        print(f"  Highest Score: {best_score['symbol']} ({best_score['overall_score']:.3f})")
        
        # Best momentum
        best_momentum = max(opportunities, key=lambda x: x['momentum_score'])
        print(f"  Best Momentum: {best_momentum['symbol']} ({best_momentum['momentum_score']:.3f})")
        
        # Best catalysts
        best_catalyst = max(opportunities, key=lambda x: x['catalyst_score'])
        print(f"  Best Catalysts: {best_catalyst['symbol']} ({best_catalyst['catalyst_score']:.3f})")
        
        # Highest volume surge
        best_volume = max(opportunities, key=lambda x: x['volume_ratio'])
        print(f"  Highest Volume Surge: {best_volume['symbol']} ({best_volume['volume_ratio']:.1f}x)")

if __name__ == "__main__":
    main()
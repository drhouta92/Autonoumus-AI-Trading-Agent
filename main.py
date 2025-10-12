"""
Micro-Cap AI Agent 2.5 - Main Entry Point
Complete autonomous trading agent with kill-gate brain evolution
"""

import pandas as pd
import numpy as np
from datetime import datetime
import config
from agent_orchestrator import AgentOrchestrator
import os
import sys

def main():
    print("=" * 70)
    print("MICRO-CAP AI AGENT 2.5")
    print("Autonomous Trading Agent with Kill-Gate Brain Evolution")
    print("=" * 70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator(config)
    
    try:
        # Run complete agent cycle
        results = orchestrator.run_full_cycle()
        
        # Extract results
        opportunities = results.get('analyzed', [])
        decisions = results.get('decisions', [])
        brain_stats = results.get('brain_stats', {})
        
        # Sort opportunities by score
        ranked_opportunities = sorted(
            opportunities,
            key=lambda x: x.get('overall_score', 0),
            reverse=True
        )
        
        # Display results
        if ranked_opportunities:
            print("\n" + "=" * 70)
            print("TOP MICRO-CAP OPPORTUNITIES")
            print("=" * 70)
            print(f"Total analyzed: {len(ranked_opportunities)}")
            print(f"Buy decisions: {len([d for d in decisions if d.action == 'BUY'])}")
            print()
            
            for i, opportunity in enumerate(ranked_opportunities[:10], 1):
                fundamentals = opportunity.get('fundamentals', {})
                technical = opportunity.get('technical', {})
                risk = opportunity.get('risk', {})
                position = opportunity.get('position')
                
                print(f"{i}. {fundamentals.get('symbol', 'N/A')}")
                print(f"   Price: ${fundamentals.get('price', 0):.3f}")
                print(f"   Market Cap: ${fundamentals.get('market_cap', 0):,.0f}")
                print(f"   Overall Score: {opportunity.get('overall_score', 0):.3f}")
                print(f"   Technical Score: {technical.get('technical_score', 0):.3f}")
                print(f"   Risk Level: {risk.get('overall_risk', 'unknown')}")
                
                if position:
                    print(f"   Suggested Position: {position.position_size} shares")
                    print(f"   Stop Loss: ${position.stop_loss:.3f}")
                    print(f"   Take Profit: ${position.take_profit:.3f}")
                    print(f"   Risk/Reward: {position.risk_reward_ratio:.2f}:1")
                
                if fundamentals.get('is_penny_stock'):
                    print(f"   ⭐ PENNY STOCK")
                if fundamentals.get('is_micro_cap'):
                    print(f"   💎 MICRO-CAP")
                
                print()
        else:
            print("\n⚠️  No qualifying opportunities found in this cycle.")
            print("The system will continue learning and adapting.")
            print()
        
        # Generate summary report
        print("=" * 70)
        print("BRAIN STATISTICS")
        print("=" * 70)
        print(f"Current Generation: {brain_stats.get('current_generation', 0)}")
        print(f"Brain Status: {brain_stats.get('current_status', 'unknown')}")
        print(f"Current Performance: {brain_stats.get('current_performance', 0):.1%}")
        print(f"Avg Performance: {brain_stats.get('avg_performance', 0):.1%}")
        print(f"Total Archived: {brain_stats.get('total_archived', 0)}")
        print()
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"microcap_ai_agent_report_{timestamp}.csv"
        
        if ranked_opportunities:
            df_data = []
            for opp in ranked_opportunities:
                fundamentals = opp.get('fundamentals', {})
                technical = opp.get('technical', {})
                risk = opp.get('risk', {})
                position = opp.get('position')
                
                df_data.append({
                    'symbol': fundamentals.get('symbol', 'N/A'),
                    'price': fundamentals.get('price', 0),
                    'market_cap': fundamentals.get('market_cap', 0),
                    'overall_score': opp.get('overall_score', 0),
                    'technical_score': technical.get('technical_score', 0),
                    'risk_level': risk.get('risk_level', 0),
                    'risk_score': risk.get('risk_score', 0),
                    'is_penny_stock': fundamentals.get('is_penny_stock', False),
                    'is_micro_cap': fundamentals.get('is_micro_cap', False),
                    'sector': fundamentals.get('sector', 'Unknown'),
                    'volatility': technical.get('volatility', {}).get('historical_vol', 0),
                    'stop_loss': position.stop_loss if position else 0,
                    'take_profit': position.take_profit if position else 0,
                    'risk_reward': position.risk_reward_ratio if position else 0
                })
            
            df = pd.DataFrame(df_data)
            df.to_csv(filename, index=False)
            print(f"📄 Report saved to {filename}")
            print()
        
        print("=" * 70)
        print("MICRO-CAP AI AGENT 2.5 - COMPLETE")
        print("=" * 70)
        print("✅ Kill-gate brain evolution active")
        print("✅ Specialized micro-cap filtering")
        print("✅ Advanced technical analysis")
        print("✅ Risk management with position sizing")
        print("✅ Offline learning applied")
        print("✅ Dual persistence (JSON + SQLite)")
        print("=" * 70)
    
    finally:
        # Graceful shutdown
        orchestrator.shutdown()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
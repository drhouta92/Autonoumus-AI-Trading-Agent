"""
Decision Engine
Final decision making for trading actions
Integrates all analysis and applies final filters
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class TradingDecision:
    """Final trading decision"""
    symbol: str
    action: str  # "BUY", "SELL", "HOLD", "PASS"
    confidence: float
    reasons: List[str]
    score_breakdown: Dict[str, float]
    position_details: Optional[Dict]
    risk_assessment: Dict
    timestamp: str

class DecisionEngine:
    """
    Final decision engine that integrates all analysis
    Applies final filters and confidence thresholds
    """
    
    def __init__(self, config, brain_manager=None):
        self.config = config
        self.brain_manager = brain_manager
        
        # Decision thresholds
        self.min_confidence = 0.65
        self.min_overall_score = 0.55
        self.max_risk_level = 4  # 1-5 scale
        
        # Scoring weights (can be updated by brain)
        self.weights = {
            'technical': 0.30,
            'momentum': 0.25,
            'catalyst': 0.20,
            'risk_adjusted': 0.15,
            'liquidity': 0.10
        }
    
    def make_decision(self, symbol: str, analysis_data: Dict) -> TradingDecision:
        """
        Make final trading decision based on all analysis
        """
        # Extract components
        technical_analysis = analysis_data.get('technical', {})
        momentum_analysis = analysis_data.get('momentum', {})
        catalyst_data = analysis_data.get('catalyst', {})
        risk_assessment = analysis_data.get('risk', {})
        position_data = analysis_data.get('position', None)
        
        # Calculate component scores
        scores = {
            'technical': self._score_technical(technical_analysis),
            'momentum': self._score_momentum(momentum_analysis),
            'catalyst': self._score_catalyst(catalyst_data),
            'risk_adjusted': self._score_risk(risk_assessment),
            'liquidity': self._score_liquidity(analysis_data)
        }
        
        # Calculate weighted overall score
        overall_score = sum(scores[k] * self.weights[k] for k in scores)
        
        # Apply brain adjustments if available
        if self.brain_manager and self.brain_manager.current_brain:
            overall_score = self._apply_brain_adjustments(overall_score, analysis_data)
        
        # Determine action and confidence
        action, confidence, reasons = self._determine_action(
            overall_score, scores, risk_assessment
        )
        
        # Create decision
        decision = TradingDecision(
            symbol=symbol,
            action=action,
            confidence=confidence,
            reasons=reasons,
            score_breakdown=scores,
            position_details=position_data,
            risk_assessment=risk_assessment,
            timestamp=datetime.now().isoformat()
        )
        
        # Record decision in brain
        if self.brain_manager:
            self.brain_manager.record_decision(symbol, action, confidence)
        
        return decision
    
    def _score_technical(self, technical: Dict) -> float:
        """Score technical analysis (0-1)"""
        if not technical:
            return 0.0
        
        score = technical.get('technical_score', 0.0)
        
        # Bonus for specific indicators
        indicators = technical.get('indicators', {})
        
        if indicators.get('rsi_signal') == 'oversold':
            score += 0.1
        if indicators.get('macd_crossover') == 'bullish_crossover':
            score += 0.15
        if indicators.get('stoch_signal') in ['oversold', 'bullish']:
            score += 0.1
        
        # Pattern bonus
        patterns = technical.get('patterns', [])
        bullish_patterns = ['hammer', 'bullish_engulfing', 'morning_star', 'breakout']
        if any(p in patterns for p in bullish_patterns):
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_momentum(self, momentum: Dict) -> float:
        """Score momentum analysis (0-1)"""
        if not momentum:
            return 0.0
        
        classification = momentum.get('classification', 'neutral')
        
        if classification == 'strong_bullish':
            return 1.0
        elif classification == 'bullish':
            return 0.75
        elif classification == 'neutral':
            return 0.5
        elif classification == 'bearish':
            return 0.25
        else:  # strong_bearish
            return 0.0
    
    def _score_catalyst(self, catalyst: Dict) -> float:
        """Score catalyst data (0-1)"""
        if not catalyst:
            return 0.5  # Neutral if no data
        
        score = 0.0
        
        # Sentiment score (-1 to 1, normalize to 0-1)
        sentiment = catalyst.get('sentiment_score', 0.0)
        score += (sentiment + 1) / 2 * 0.5
        
        # Buzz score (0-1)
        buzz = catalyst.get('buzz_score', 0.0)
        score += buzz * 0.3
        
        # News count bonus
        news_count = catalyst.get('news_count', 0)
        if news_count > 10:
            score += 0.2
        elif news_count > 5:
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_risk(self, risk: Dict) -> float:
        """Score risk assessment (0-1, higher is better)"""
        if not risk:
            return 0.5
        
        risk_level = risk.get('risk_level', 3)  # 1-5 scale
        
        # Invert risk level (lower risk = higher score)
        score = (6 - risk_level) / 5.0
        
        # Adjust for specific risk factors
        risk_factors = risk.get('risk_factors', [])
        
        # Penalize extreme risks
        if 'nano_cap_extreme_risk' in risk_factors:
            score *= 0.5
        if 'very_low_liquidity' in risk_factors:
            score *= 0.7
        
        return max(score, 0.0)
    
    def _score_liquidity(self, analysis_data: Dict) -> float:
        """Score liquidity (0-1)"""
        position = analysis_data.get('position')
        if position and hasattr(position, 'liquidity_score'):
            return position.liquidity_score
        
        # Alternative: use volume data
        volume_analysis = analysis_data.get('technical', {}).get('volume_analysis', {})
        volume_ratio = volume_analysis.get('volume_ratio', 1.0)
        
        if volume_ratio > 2.0:
            return 1.0
        elif volume_ratio > 1.5:
            return 0.8
        elif volume_ratio > 1.0:
            return 0.6
        else:
            return 0.4
    
    def _apply_brain_adjustments(self, score: float, analysis_data: Dict) -> float:
        """Apply brain learning adjustments"""
        brain = self.brain_manager.current_brain
        
        # Adjust based on learned patterns
        learned = brain.learned_patterns
        
        # Sector boost
        sector = analysis_data.get('fundamentals', {}).get('sector', '')
        if sector in learned.get('successful_sectors', []):
            score *= 1.1
        
        # Pattern boost
        patterns = analysis_data.get('technical', {}).get('patterns', [])
        successful_patterns = learned.get('successful_patterns', [])
        if any(p in successful_patterns for p in patterns):
            score *= 1.05
        
        # Avoid failed symbols
        symbol = analysis_data.get('symbol', '')
        if symbol in learned.get('failed_symbols', []):
            score *= 0.8
        
        return min(score, 1.0)
    
    def _determine_action(self, overall_score: float, scores: Dict,
                         risk_assessment: Dict) -> Tuple[str, float, List[str]]:
        """
        Determine action, confidence, and reasons
        """
        reasons = []
        
        # Check if meets minimum thresholds
        if overall_score < self.min_overall_score:
            return "PASS", overall_score, ["score_below_threshold"]
        
        # Check risk level
        risk_level = risk_assessment.get('risk_level', 3)
        if risk_level > self.max_risk_level:
            return "PASS", overall_score, ["risk_too_high"]
        
        # Check individual components
        if scores['technical'] < 0.4:
            return "PASS", overall_score, ["weak_technicals"]
        
        if scores['liquidity'] < 0.3:
            return "PASS", overall_score, ["insufficient_liquidity"]
        
        # Determine action based on score
        if overall_score >= 0.75:
            action = "BUY"
            confidence = min(overall_score, 0.95)
            reasons.extend([
                f"strong_overall_score_{overall_score:.2f}",
                f"technical_{scores['technical']:.2f}",
                f"momentum_{scores['momentum']:.2f}"
            ])
        elif overall_score >= 0.65:
            action = "BUY"
            confidence = overall_score
            reasons.extend([
                f"good_overall_score_{overall_score:.2f}",
                f"acceptable_risk_level_{risk_level}"
            ])
        elif overall_score >= 0.55:
            action = "HOLD"
            confidence = overall_score * 0.8
            reasons.extend([
                f"moderate_score_{overall_score:.2f}",
                "waiting_for_better_setup"
            ])
        else:
            action = "PASS"
            confidence = overall_score
            reasons.append("score_insufficient")
        
        return action, confidence, reasons
    
    def batch_decisions(self, opportunities: List[Dict]) -> List[TradingDecision]:
        """
        Make decisions for multiple opportunities
        """
        decisions = []
        
        for opp in opportunities:
            try:
                decision = self.make_decision(
                    symbol=opp.get('symbol', ''),
                    analysis_data=opp
                )
                decisions.append(decision)
            except Exception as e:
                print(f"Error making decision for {opp.get('symbol', 'unknown')}: {e}")
        
        return decisions
    
    def filter_decisions(self, decisions: List[TradingDecision],
                        action_filter: str = "BUY") -> List[TradingDecision]:
        """
        Filter decisions by action and sort by confidence
        """
        filtered = [d for d in decisions if d.action == action_filter]
        filtered.sort(key=lambda x: x.confidence, reverse=True)
        return filtered
    
    def explain_decision(self, decision: TradingDecision) -> str:
        """
        Generate human-readable explanation of decision
        """
        explanation = []
        explanation.append(f"Symbol: {decision.symbol}")
        explanation.append(f"Action: {decision.action}")
        explanation.append(f"Confidence: {decision.confidence:.1%}")
        explanation.append(f"Timestamp: {decision.timestamp}")
        explanation.append("")
        explanation.append("Score Breakdown:")
        for component, score in decision.score_breakdown.items():
            explanation.append(f"  {component}: {score:.3f}")
        explanation.append("")
        explanation.append("Reasons:")
        for reason in decision.reasons:
            explanation.append(f"  - {reason}")
        explanation.append("")
        explanation.append("Risk Assessment:")
        risk = decision.risk_assessment
        explanation.append(f"  Overall Risk: {risk.get('overall_risk', 'unknown')}")
        explanation.append(f"  Risk Score: {risk.get('risk_score', 0):.3f}")
        
        if decision.position_details:
            explanation.append("")
            explanation.append("Position Details:")
            pos = decision.position_details
            if hasattr(pos, 'position_size'):
                explanation.append(f"  Position Size: {pos.position_size} shares")
                explanation.append(f"  Stop Loss: ${pos.stop_loss:.3f}")
                explanation.append(f"  Take Profit: ${pos.take_profit:.3f}")
                explanation.append(f"  Risk/Reward: {pos.risk_reward_ratio:.2f}:1")
        
        return "\n".join(explanation)

# Example usage
if __name__ == "__main__":
    import config
    
    engine = DecisionEngine(config)
    
    # Example analysis data
    analysis = {
        'symbol': 'TEST',
        'technical': {'technical_score': 0.75, 'patterns': ['breakout']},
        'momentum': {'classification': 'bullish'},
        'catalyst': {'sentiment_score': 0.5, 'buzz_score': 0.7},
        'risk': {'risk_level': 3, 'overall_risk': 'moderate'},
        'fundamentals': {'sector': 'Technology'}
    }
    
    decision = engine.make_decision('TEST', analysis)
    print(engine.explain_decision(decision))

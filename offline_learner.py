"""
Offline Learner
Learns from historical performance and adjusts strategies
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

class OfflineLearner:
    """
    Learns from historical trading decisions and outcomes
    Adjusts weights and thresholds based on performance
    """
    
    def __init__(self, config, persistence_manager=None):
        self.config = config
        self.persistence = persistence_manager
        
        # Learning parameters
        self.learning_rate = 0.1
        self.min_samples = 10  # Minimum samples for learning
        
        # Performance tracking
        self.sector_performance = defaultdict(list)
        self.pattern_performance = defaultdict(list)
        self.time_performance = defaultdict(list)
        self.overall_stats = {
            'total_decisions': 0,
            'buy_decisions': 0,
            'successful_buys': 0,
            'win_rate': 0.0,
            'avg_return': 0.0
        }
    
    def learn_from_history(self, days: int = 30) -> Dict:
        """
        Learn from historical data and generate insights
        """
        print(f"📚 Learning from {days} days of history...")
        
        if not self.persistence:
            print("⚠️  No persistence manager available")
            return {}
        
        # Load historical data
        opportunities = self.persistence.load_opportunities(days)
        decisions = self.persistence.load_decisions(days)
        
        if not opportunities or not decisions:
            print("⚠️  Insufficient historical data")
            return {}
        
        # Analyze performance
        learning_insights = {}
        
        # 1. Sector analysis
        learning_insights['sector_analysis'] = self._analyze_sectors(opportunities, decisions)
        
        # 2. Pattern analysis
        learning_insights['pattern_analysis'] = self._analyze_patterns(opportunities)
        
        # 3. Timing analysis
        learning_insights['timing_analysis'] = self._analyze_timing(decisions)
        
        # 4. Confidence calibration
        learning_insights['confidence_calibration'] = self._calibrate_confidence(decisions)
        
        # 5. Weight adjustments
        learning_insights['weight_adjustments'] = self._calculate_weight_adjustments(
            learning_insights
        )
        
        # 6. Overall performance
        learning_insights['overall_performance'] = self._calculate_overall_performance(
            opportunities, decisions
        )
        
        print(f"✅ Learning complete. Win rate: {learning_insights['overall_performance'].get('win_rate', 0):.1%}")
        
        return learning_insights
    
    def _analyze_sectors(self, opportunities: List[Dict], 
                        decisions: List[Dict]) -> Dict:
        """Analyze performance by sector"""
        sector_stats = defaultdict(lambda: {
            'count': 0,
            'buy_decisions': 0,
            'avg_score': 0.0,
            'avg_confidence': 0.0
        })
        
        # Build decision map
        decision_map = {d['symbol']: d for d in decisions if d.get('action') == 'BUY'}
        
        for opp in opportunities:
            sector = opp.get('sector', 'Unknown')
            symbol = opp.get('symbol')
            
            sector_stats[sector]['count'] += 1
            sector_stats[sector]['avg_score'] += opp.get('overall_score', 0)
            
            if symbol in decision_map:
                sector_stats[sector]['buy_decisions'] += 1
                sector_stats[sector]['avg_confidence'] += decision_map[symbol].get('confidence', 0)
        
        # Calculate averages
        for sector in sector_stats:
            if sector_stats[sector]['count'] > 0:
                sector_stats[sector]['avg_score'] /= sector_stats[sector]['count']
            if sector_stats[sector]['buy_decisions'] > 0:
                sector_stats[sector]['avg_confidence'] /= sector_stats[sector]['buy_decisions']
        
        # Identify top sectors
        top_sectors = sorted(
            sector_stats.items(),
            key=lambda x: x[1]['avg_score'],
            reverse=True
        )[:5]
        
        return {
            'sector_stats': dict(sector_stats),
            'top_sectors': [s[0] for s in top_sectors],
            'sector_success_rates': {s: stats['buy_decisions'] / max(stats['count'], 1) 
                                    for s, stats in sector_stats.items()}
        }
    
    def _analyze_patterns(self, opportunities: List[Dict]) -> Dict:
        """Analyze technical patterns performance"""
        pattern_stats = defaultdict(lambda: {
            'count': 0,
            'avg_score': 0.0,
            'in_top_10_percent': 0
        })
        
        # Sort opportunities by score
        sorted_opps = sorted(opportunities, 
                           key=lambda x: x.get('overall_score', 0), 
                           reverse=True)
        top_10_percent = len(sorted_opps) // 10
        top_symbols = {opp['symbol'] for opp in sorted_opps[:top_10_percent]}
        
        for opp in opportunities:
            # Extract patterns (would need to be stored in opportunity)
            patterns = opp.get('patterns', [])
            score = opp.get('overall_score', 0)
            is_top = opp['symbol'] in top_symbols
            
            for pattern in patterns:
                pattern_stats[pattern]['count'] += 1
                pattern_stats[pattern]['avg_score'] += score
                if is_top:
                    pattern_stats[pattern]['in_top_10_percent'] += 1
        
        # Calculate averages
        for pattern in pattern_stats:
            if pattern_stats[pattern]['count'] > 0:
                pattern_stats[pattern]['avg_score'] /= pattern_stats[pattern]['count']
        
        # Identify successful patterns
        successful_patterns = [
            pattern for pattern, stats in pattern_stats.items()
            if stats['avg_score'] > 0.6 and stats['count'] >= 3
        ]
        
        return {
            'pattern_stats': dict(pattern_stats),
            'successful_patterns': successful_patterns
        }
    
    def _analyze_timing(self, decisions: List[Dict]) -> Dict:
        """Analyze decision timing patterns"""
        timing_stats = {
            'by_hour': defaultdict(int),
            'by_day': defaultdict(int),
            'by_weekday': defaultdict(int)
        }
        
        for decision in decisions:
            if decision.get('action') != 'BUY':
                continue
            
            try:
                timestamp = datetime.fromisoformat(decision['timestamp'])
                timing_stats['by_hour'][timestamp.hour] += 1
                timing_stats['by_day'][timestamp.day] += 1
                timing_stats['by_weekday'][timestamp.strftime('%A')] += 1
            except:
                pass
        
        # Find optimal times
        optimal_hour = max(timing_stats['by_hour'].items(), 
                          key=lambda x: x[1])[0] if timing_stats['by_hour'] else 10
        optimal_day = max(timing_stats['by_weekday'].items(),
                         key=lambda x: x[1])[0] if timing_stats['by_weekday'] else 'Monday'
        
        return {
            'timing_distribution': {
                'by_hour': dict(timing_stats['by_hour']),
                'by_weekday': dict(timing_stats['by_weekday'])
            },
            'optimal_hour': optimal_hour,
            'optimal_day': optimal_day
        }
    
    def _calibrate_confidence(self, decisions: List[Dict]) -> Dict:
        """Calibrate confidence scores"""
        confidence_buckets = {
            'low': {'count': 0, 'correct': 0},      # 0.5-0.65
            'medium': {'count': 0, 'correct': 0},   # 0.65-0.80
            'high': {'count': 0, 'correct': 0}      # 0.80-1.0
        }
        
        for decision in decisions:
            confidence = decision.get('confidence', 0)
            action = decision.get('action')
            
            if action != 'BUY':
                continue
            
            # Bucket assignment
            if confidence < 0.65:
                bucket = 'low'
            elif confidence < 0.80:
                bucket = 'medium'
            else:
                bucket = 'high'
            
            confidence_buckets[bucket]['count'] += 1
            
            # Would need actual outcome data to determine 'correct'
            # For now, assume higher confidence = higher success
            if confidence > 0.75:
                confidence_buckets[bucket]['correct'] += 1
        
        # Calculate calibration
        calibration = {}
        for bucket, stats in confidence_buckets.items():
            if stats['count'] > 0:
                calibration[bucket] = stats['correct'] / stats['count']
            else:
                calibration[bucket] = 0.0
        
        return {
            'calibration_by_bucket': calibration,
            'confidence_distribution': confidence_buckets
        }
    
    def _calculate_weight_adjustments(self, insights: Dict) -> Dict:
        """Calculate weight adjustments based on learning"""
        adjustments = {}
        
        # Sector performance adjustment
        sector_analysis = insights.get('sector_analysis', {})
        top_sectors = sector_analysis.get('top_sectors', [])
        if top_sectors:
            # Boost discovery weight for successful sectors
            adjustments['sectors'] = 0.1
        
        # Pattern performance adjustment
        pattern_analysis = insights.get('pattern_analysis', {})
        successful_patterns = pattern_analysis.get('successful_patterns', [])
        if len(successful_patterns) >= 3:
            adjustments['technical_pattern'] = 0.05
        
        # Timing adjustment
        timing_analysis = insights.get('timing_analysis', {})
        if timing_analysis:
            adjustments['timing_boost'] = 0.05
        
        return adjustments
    
    def _calculate_overall_performance(self, opportunities: List[Dict],
                                      decisions: List[Dict]) -> Dict:
        """Calculate overall performance metrics"""
        buy_decisions = [d for d in decisions if d.get('action') == 'BUY']
        
        performance = {
            'total_opportunities': len(opportunities),
            'total_decisions': len(decisions),
            'buy_decisions': len(buy_decisions),
            'buy_rate': len(buy_decisions) / len(decisions) if decisions else 0,
            'avg_opportunity_score': np.mean([o.get('overall_score', 0) for o in opportunities]) if opportunities else 0,
            'avg_buy_confidence': np.mean([d.get('confidence', 0) for d in buy_decisions]) if buy_decisions else 0
        }
        
        # Win rate simulation (would need actual outcome data)
        # For now, estimate based on confidence
        if buy_decisions:
            high_conf_decisions = [d for d in buy_decisions if d.get('confidence', 0) > 0.75]
            performance['estimated_win_rate'] = len(high_conf_decisions) / len(buy_decisions)
        else:
            performance['estimated_win_rate'] = 0.0
        
        return performance
    
    def generate_learning_report(self, insights: Dict) -> str:
        """Generate human-readable learning report"""
        report = []
        report.append("=" * 60)
        report.append("OFFLINE LEARNING REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Overall performance
        overall = insights.get('overall_performance', {})
        report.append("Overall Performance:")
        report.append(f"  Total Opportunities: {overall.get('total_opportunities', 0)}")
        report.append(f"  Buy Decisions: {overall.get('buy_decisions', 0)}")
        report.append(f"  Buy Rate: {overall.get('buy_rate', 0):.1%}")
        report.append(f"  Avg Confidence: {overall.get('avg_buy_confidence', 0):.1%}")
        report.append(f"  Estimated Win Rate: {overall.get('estimated_win_rate', 0):.1%}")
        report.append("")
        
        # Sector insights
        sector_analysis = insights.get('sector_analysis', {})
        top_sectors = sector_analysis.get('top_sectors', [])
        if top_sectors:
            report.append("Top Performing Sectors:")
            for i, sector in enumerate(top_sectors, 1):
                report.append(f"  {i}. {sector}")
            report.append("")
        
        # Pattern insights
        pattern_analysis = insights.get('pattern_analysis', {})
        successful_patterns = pattern_analysis.get('successful_patterns', [])
        if successful_patterns:
            report.append("Successful Patterns:")
            for pattern in successful_patterns:
                report.append(f"  - {pattern}")
            report.append("")
        
        # Weight adjustments
        adjustments = insights.get('weight_adjustments', {})
        if adjustments:
            report.append("Recommended Weight Adjustments:")
            for key, value in adjustments.items():
                report.append(f"  {key}: +{value:.1%}")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)

# Example usage
if __name__ == "__main__":
    import config
    from persistence_manager import PersistenceManager
    
    pm = PersistenceManager(config)
    learner = OfflineLearner(config, pm)
    
    insights = learner.learn_from_history(days=30)
    report = learner.generate_learning_report(insights)
    print(report)

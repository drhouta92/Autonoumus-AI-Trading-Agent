"""
Reinforcement Learning module for autonomous trading agent
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
import joblib
import os
from datetime import datetime
from collections import deque
import random

class ReinforcementLearner:
    def __init__(self, config):
        self.config = config
        self.learning_rate = 0.001
        self.discount_factor = 0.95
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 32
        self.memory = deque(maxlen=2000)
        self.model_path = "models/rl_model.pkl"
        self.feature_columns = [
            'momentum_score', 'catalyst_score', 'sentiment_score', 
            'volume_ratio', 'risk_reward_ratio', 'beta', 
            'pe_ratio', 'price_change_pct', 'rsi', 'macd'
        ]
        self.q_table = {}  # State-action value table
        self.performance_history = []
        self.load_model()
    
    def load_model(self) -> None:
        """Load existing model if available"""
        try:
            if os.path.exists(self.model_path):
                self.q_table = joblib.load(self.model_path)
                print(f"Loaded existing RL model with {len(self.q_table)} state-action pairs")
        except Exception as e:
            print(f"Could not load RL model: {e}")
            self.q_table = {}
    
    def save_model(self) -> None:
        """Save model to disk"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.q_table, self.model_path)
            print(f"Saved RL model with {len(self.q_table)} state-action pairs")
        except Exception as e:
            print(f"Could not save RL model: {e}")
    
    def get_state_representation(self, opportunity: Dict) -> str:
        """
        Convert an opportunity to a discretized state representation
        """
        # Discretize continuous features into buckets for state representation
        state_components = []
        
        # Momentum score (5 buckets)
        momentum = opportunity.get('momentum_score', 0)
        momentum_bucket = min(int(momentum * 5), 4)
        state_components.append(f"m{momentum_bucket}")
        
        # Catalyst score (5 buckets)
        catalyst = opportunity.get('catalyst_score', 0)
        catalyst_bucket = min(int(catalyst * 5), 4)
        state_components.append(f"c{catalyst_bucket}")
        
        # Volume ratio (5 buckets: 1x, 1-2x, 2-3x, 3-5x, >5x)
        volume_ratio = opportunity.get('volume_ratio', 1.0)
        if volume_ratio < 1:
            vol_bucket = 0
        elif volume_ratio < 2:
            vol_bucket = 1
        elif volume_ratio < 3:
            vol_bucket = 2
        elif volume_ratio < 5:
            vol_bucket = 3
        else:
            vol_bucket = 4
        state_components.append(f"v{vol_bucket}")
        
        # Risk/reward ratio (4 buckets: <1, 1-2, 2-3, >3)
        risk_reward = opportunity.get('risk_reward_ratio', 1.0)
        if risk_reward < 1:
            rr_bucket = 0
        elif risk_reward < 2:
            rr_bucket = 1
        elif risk_reward < 3:
            rr_bucket = 2
        else:
            rr_bucket = 3
        state_components.append(f"r{rr_bucket}")
        
        # Market cap category (4 buckets: micro, small, mid, large)
        market_cap = opportunity.get('market_cap', 0)
        if market_cap < 300_000_000:
            cap_bucket = 0  # Micro cap
        elif market_cap < 2_000_000_000:
            cap_bucket = 1  # Small cap
        elif market_cap < 10_000_000_000:
            cap_bucket = 2  # Mid cap
        else:
            cap_bucket = 3  # Large cap
        state_components.append(f"cap{cap_bucket}")
        
        # Join components to create state string
        return "_".join(state_components)
    
    def get_action(self, state: str, explore: bool = True) -> int:
        """
        Get action (0: Skip, 1: Trade) using epsilon-greedy policy
        """
        # Exploration
        if explore and np.random.rand() < self.epsilon:
            return np.random.choice([0, 1])
        
        # Exploitation - use learned Q-values
        if state not in self.q_table:
            self.q_table[state] = [0, 0]  # Initialize Q-values for new state
            
        return np.argmax(self.q_table[state])
    
    def update_q_table(self, state: str, action: int, reward: float, next_state: str) -> None:
        """
        Update Q-value using Q-learning update rule
        """
        if state not in self.q_table:
            self.q_table[state] = [0, 0]
            
        if next_state not in self.q_table:
            self.q_table[next_state] = [0, 0]
        
        # Q-learning update formula
        current_q = self.q_table[state][action]
        max_next_q = max(self.q_table[next_state])
        
        # Q(s,a) = Q(s,a) + α * (r + γ * max_a' Q(s',a') - Q(s,a))
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state][action] = new_q
    
    def remember(self, state: str, action: int, reward: float, next_state: str) -> None:
        """Store experience in memory for batch learning"""
        self.memory.append((state, action, reward, next_state))
    
    def replay(self, batch_size: int = None) -> None:
        """Learn from past experiences with batch learning"""
        if batch_size is None:
            batch_size = self.batch_size
            
        if len(self.memory) < batch_size:
            return
            
        # Sample random batch from memory
        minibatch = random.sample(self.memory, batch_size)
        
        for state, action, reward, next_state in minibatch:
            self.update_q_table(state, action, reward, next_state)
        
        # Decay exploration rate
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def calculate_reward(self, opportunity: Dict, outcome: Dict) -> float:
        """
        Calculate reward based on trading outcome
        """
        if not opportunity or not outcome:
            return -0.1  # Penalty for missing data
        
        # Extract outcome metrics
        profit_loss_pct = outcome.get('profit_loss_pct', 0)
        hit_target = outcome.get('hit_target', False)
        hit_stop_loss = outcome.get('hit_stop_loss', False)
        hold_time_days = outcome.get('hold_time_days', 0)
        
        # Base reward on profit/loss
        if profit_loss_pct > 0:
            # Profitable trade - reward proportional to profit
            reward = min(profit_loss_pct / 10, 1.0)  # Cap at 1.0 for 10% profit
        else:
            # Losing trade - penalty proportional to loss
            reward = max(profit_loss_pct / 5, -1.0)  # Cap at -1.0 for 5% loss
        
        # Additional reward components
        if hit_target:
            reward += 0.5  # Bonus for hitting target
        if hit_stop_loss:
            reward -= 0.2  # Additional penalty for hitting stop loss
        
        # Time efficiency factor (higher reward for quicker profits)
        if profit_loss_pct > 0 and hold_time_days > 0:
            time_factor = 7 / max(hold_time_days, 7)  # 1.0 for ≤7 days, less for longer
            reward *= time_factor
        
        return reward
    
    def evaluate_performance(self, trade_history: List[Dict]) -> Dict:
        """
        Evaluate agent's performance based on trade history
        """
        if not trade_history:
            return {
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'total_return': 0
            }
            
        wins = [t for t in trade_history if t.get('profit_loss_pct', 0) > 0]
        losses = [t for t in trade_history if t.get('profit_loss_pct', 0) <= 0]
        
        win_rate = len(wins) / len(trade_history) if trade_history else 0
        avg_profit = np.mean([t.get('profit_loss_pct', 0) for t in wins]) if wins else 0
        avg_loss = np.mean([abs(t.get('profit_loss_pct', 0)) for t in losses]) if losses else 0
        
        total_profit = sum([t.get('profit_loss_pct', 0) for t in wins]) if wins else 0
        total_loss = sum([abs(t.get('profit_loss_pct', 0)) for t in losses]) if losses else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        total_return = sum([t.get('profit_loss_pct', 0) for t in trade_history])
        
        performance = {
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_return': total_return,
            'trade_count': len(trade_history)
        }
        
        # Track performance history
        self.performance_history.append({
            'timestamp': datetime.now(),
            'metrics': performance
        })
        
        return performance
    
    def learn_from_historical_trades(self, historical_trades: List[Dict]) -> None:
        """
        Learn from historical trading data
        """
        print(f"Learning from {len(historical_trades)} historical trades...")
        
        for trade in historical_trades:
            opportunity = trade.get('opportunity', {})
            outcome = trade.get('outcome', {})
            
            if not opportunity or not outcome:
                continue
                
            state = self.get_state_representation(opportunity)
            action = 1  # Action was to trade
            reward = self.calculate_reward(opportunity, outcome)
            
            # Use the same state as next state since we're learning from completed trades
            self.update_q_table(state, action, reward, state)
        
        print(f"Updated Q-table based on historical trades. Table now has {len(self.q_table)} states.")
        self.save_model()
    
    def update_discovery_parameters(self, autonomous_discovery) -> None:
        """
        Update discovery parameters based on learning
        """
        # Extract performance data to guide parameter updates
        if not self.performance_history:
            return
            
        recent_performance = self.performance_history[-1]['metrics']
        win_rate = recent_performance.get('win_rate', 0)
        
        # Adjust discovery parameters based on performance
        if win_rate > 0.6:  # If doing well, be more selective
            autonomous_discovery.config.CONFIDENCE_THRESHOLD = min(
                autonomous_discovery.config.CONFIDENCE_THRESHOLD + 0.05, 0.85
            )
        elif win_rate < 0.4:  # If doing poorly, be less selective
            autonomous_discovery.config.CONFIDENCE_THRESHOLD = max(
                autonomous_discovery.config.CONFIDENCE_THRESHOLD - 0.05, 0.5
            )
            
        # Print update
        print(f"Updated discovery confidence threshold to {autonomous_discovery.config.CONFIDENCE_THRESHOLD}")
    
    def rank_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """
        Rank opportunities based on learned preferences
        """
        ranked_opportunities = []
        
        for opp in opportunities:
            state = self.get_state_representation(opp)
            
            # Get Q-value for trading this opportunity
            if state in self.q_table:
                q_value = self.q_table[state][1]  # Q-value for action 1 (trade)
            else:
                q_value = 0  # Default for new states
            
            # Add Q-value to opportunity data
            opp_with_q = opp.copy()
            opp_with_q['q_value'] = q_value
            ranked_opportunities.append(opp_with_q)
        
        # Sort by Q-value and overall score
        return sorted(
            ranked_opportunities, 
            key=lambda x: (x.get('q_value', 0) * 0.7 + x.get('overall_score', 0) * 0.3),
            reverse=True
        )
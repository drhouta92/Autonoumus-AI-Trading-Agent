"""
Risk management module for truly autonomous AI trading agent
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class PositionSizeMethod(Enum):
    FIXED_FRACTIONAL = "fixed_fractional"
    VOLATILITY_ADJUSTED = "volatility_adjusted"

@dataclass
class Position:
    symbol: str
    size: float
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_amount: float
    reward_amount: float
    risk_reward_ratio: float

class RiskManager:
    def __init__(self, config):
        self.config = config
        self.portfolio_value = 100000.0  # Default portfolio value
        self.max_positions = 20
        self.current_positions = {}
    
    def set_portfolio_value(self, value: float):
        """Set current portfolio value"""
        self.portfolio_value = value
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                              stop_loss: float, method: PositionSizeMethod = PositionSizeMethod.FIXED_FRACTIONAL,
                              volatility: float = None) -> float:
        """
        Calculate appropriate position size based on risk management rules
        """
        if entry_price <= 0 or stop_loss <= 0:
            return 0.0
        
        risk_per_share = abs(entry_price - stop_loss)
        if risk_per_share <= 0:
            return 0.0
        
        # Maximum risk per trade
        max_risk_amount = self.portfolio_value * self.config.MAX_PORTFOLIO_RISK
        
        if method == PositionSizeMethod.FIXED_FRACTIONAL:
            # Fixed fractional method
            position_size = max_risk_amount / risk_per_share
            max_position_value = self.portfolio_value * self.config.MAX_POSITION_SIZE
            max_shares_by_value = max_position_value / entry_price
            position_size = min(position_size, max_shares_by_value)
            
        elif method == PositionSizeMethod.VOLATILITY_ADJUSTED:
            # Adjust position size based on volatility
            if volatility is None:
                volatility = 0.2  # Default 20% annualized volatility
            
            vol_adjustment = max(0.5, min(2.0, 0.2 / volatility))  # Inverse relationship
            position_size = (max_risk_amount / risk_per_share) * vol_adjustment
            
        return max(0, round(position_size))
    
    def calculate_stop_loss(self, entry_price: float, volatility: float = None, 
                           atr: float = None) -> float:
        """
        Calculate stop loss level based on various risk factors
        """
        if volatility is None:
            volatility = 0.2  # Default annualized volatility
            
        if atr is None:
            # Estimate ATR based on volatility
            atr = entry_price * (volatility / np.sqrt(252)) * 2  # 2-day ATR estimate
        
        # Stop loss based on ATR (typically 1.5-2x ATR)
        stop_loss_distance = atr * 1.5
        stop_loss = entry_price - stop_loss_distance
        
        # Also consider fixed percentage stop
        fixed_stop = entry_price * (1 - self.config.STOP_LOSS_PERCENT)
        
        # Use the more conservative (tighter) stop
        return max(stop_loss, fixed_stop)
    
    def calculate_take_profit(self, entry_price: float, stop_loss: float, 
                            risk_reward_ratio: float = 2.0) -> float:
        """
        Calculate take profit level based on risk-reward ratio
        """
        risk_amount = abs(entry_price - stop_loss)
        take_profit = entry_price + (risk_amount * risk_reward_ratio)
        return take_profit
    
    def calculate_risk_reward_ratio(self, entry_price: float, stop_loss: float, 
                                  take_profit: float) -> float:
        """
        Calculate risk-reward ratio for a trade
        """
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        
        if risk <= 0:
            return float('inf')
        
        return reward / risk

# Example usage
if __name__ == "__main__":
    pass
"""
Micro-Cap Risk Manager
Specialized risk management for micro-cap and penny stocks
Handles high volatility and liquidity concerns
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class MicroCapPosition:
    """Position details for micro-cap stock"""
    symbol: str
    entry_price: float
    position_size: int
    stop_loss: float
    take_profit: float
    max_loss_amount: float
    max_profit_amount: float
    risk_reward_ratio: float
    liquidity_score: float
    volatility_adjusted: bool

class MicroCapRiskManager:
    """
    Specialized risk management for micro-cap stocks
    - Higher stop losses for volatility
    - Liquidity-based position sizing
    - Penny stock specific rules
    """
    
    def __init__(self, config, portfolio_value: float = 100000.0):
        self.config = config
        self.portfolio_value = portfolio_value
        
        # Micro-cap specific parameters
        self.max_position_percent = 0.02  # 2% max per position (conservative)
        self.max_portfolio_risk = 0.05    # 5% total portfolio risk (higher for micro-caps)
        self.min_risk_reward = 2.0        # Minimum 2:1 reward:risk
        
        # Penny stock parameters
        self.penny_max_position = 0.01    # 1% max for penny stocks
        self.penny_stop_loss_pct = 0.25   # 25% stop for penny stocks
        self.penny_take_profit_pct = 0.75 # 75% target for penny stocks
        
        # Regular micro-cap parameters
        self.micro_stop_loss_pct = 0.15   # 15% stop for micro-caps
        self.micro_take_profit_pct = 0.45 # 45% target for micro-caps
        
        # Liquidity thresholds
        self.min_liquidity_ratio = 0.01   # Position should be < 1% of daily volume
        self.preferred_liquidity_ratio = 0.005  # Preferred < 0.5% of daily volume
        
    def calculate_position(self, symbol: str, entry_price: float, 
                          market_cap: float, avg_volume: int,
                          volatility: float, is_penny: bool) -> Optional[MicroCapPosition]:
        """
        Calculate optimal position size and risk parameters
        """
        if entry_price <= 0 or avg_volume <= 0:
            return None
        
        # Determine position limits based on stock type
        max_position_pct = self.penny_max_position if is_penny else self.max_position_percent
        stop_loss_pct = self.penny_stop_loss_pct if is_penny else self.micro_stop_loss_pct
        take_profit_pct = self.penny_take_profit_pct if is_penny else self.micro_take_profit_pct
        
        # Adjust for volatility
        if volatility > 0.8:  # High volatility
            stop_loss_pct *= 1.5
            take_profit_pct *= 1.5
        elif volatility > 0.5:  # Moderate-high volatility
            stop_loss_pct *= 1.2
            take_profit_pct *= 1.2
        
        # Calculate position size based on risk
        max_risk_amount = self.portfolio_value * max_position_pct
        stop_loss_price = entry_price * (1 - stop_loss_pct)
        risk_per_share = entry_price - stop_loss_price
        
        if risk_per_share <= 0:
            return None
        
        # Initial position size from risk management
        shares_from_risk = int(max_risk_amount / risk_per_share)
        
        # Liquidity constraint
        max_shares_liquidity = int(avg_volume * self.min_liquidity_ratio)
        preferred_shares_liquidity = int(avg_volume * self.preferred_liquidity_ratio)
        
        # Take the minimum to ensure we don't exceed any limit
        shares = min(shares_from_risk, max_shares_liquidity)
        
        # Ensure we have at least some position
        if shares < 1:
            return None
        
        # Apply liquidity score
        liquidity_score = self._calculate_liquidity_score(
            shares, avg_volume, preferred_shares_liquidity
        )
        
        # Calculate final position details
        take_profit_price = entry_price * (1 + take_profit_pct)
        max_loss = shares * risk_per_share
        max_profit = shares * (take_profit_price - entry_price)
        risk_reward = max_profit / max_loss if max_loss > 0 else 0
        
        # Validate risk/reward
        if risk_reward < self.min_risk_reward:
            # Adjust take profit to meet minimum R:R
            take_profit_price = entry_price + (risk_per_share * self.min_risk_reward)
            max_profit = shares * (take_profit_price - entry_price)
            risk_reward = self.min_risk_reward
        
        return MicroCapPosition(
            symbol=symbol,
            entry_price=entry_price,
            position_size=shares,
            stop_loss=stop_loss_price,
            take_profit=take_profit_price,
            max_loss_amount=max_loss,
            max_profit_amount=max_profit,
            risk_reward_ratio=risk_reward,
            liquidity_score=liquidity_score,
            volatility_adjusted=volatility > 0.5
        )
    
    def _calculate_liquidity_score(self, shares: int, avg_volume: int, 
                                   preferred_shares: int) -> float:
        """
        Calculate liquidity score (0-1)
        Higher is better
        """
        if avg_volume == 0:
            return 0.0
        
        position_ratio = shares / avg_volume
        
        if shares <= preferred_shares:
            return 1.0  # Excellent liquidity
        elif shares <= avg_volume * 0.01:
            return 0.7  # Good liquidity
        elif shares <= avg_volume * 0.02:
            return 0.5  # Acceptable liquidity
        elif shares <= avg_volume * 0.05:
            return 0.3  # Poor liquidity
        else:
            return 0.1  # Very poor liquidity
    
    def calculate_dynamic_stops(self, symbol: str, entry_price: float,
                               current_price: float, atr: float,
                               is_penny: bool) -> Dict[str, float]:
        """
        Calculate dynamic stop loss using ATR
        Useful for trailing stops
        """
        stops = {}
        
        # ATR-based stop
        if atr > 0:
            atr_multiplier = 2.5 if is_penny else 2.0
            stops['atr_stop'] = current_price - (atr * atr_multiplier)
        
        # Percentage-based stop
        stop_pct = self.penny_stop_loss_pct if is_penny else self.micro_stop_loss_pct
        stops['percent_stop'] = entry_price * (1 - stop_pct)
        
        # Trailing stop (if in profit)
        if current_price > entry_price:
            profit_pct = (current_price - entry_price) / entry_price
            # Trail at 50% of profit
            trailing_distance = current_price * (profit_pct * 0.5)
            stops['trailing_stop'] = current_price - trailing_distance
        
        # Use the highest stop (most conservative)
        stops['recommended_stop'] = max(stops.values())
        
        return stops
    
    def assess_micro_cap_risk(self, symbol: str, market_cap: float,
                              price: float, avg_volume: int,
                              volatility: float, beta: float) -> Dict:
        """
        Comprehensive risk assessment for micro-cap
        """
        risk_assessment = {
            'overall_risk': 'unknown',
            'risk_score': 0.0,
            'risk_factors': [],
            'risk_level': 0  # 1-5 scale
        }
        
        risk_score = 0.0
        risk_factors = []
        
        # Market cap risk
        if market_cap < 10_000_000:  # < $10M
            risk_score += 0.3
            risk_factors.append("nano_cap_extreme_risk")
        elif market_cap < 50_000_000:  # < $50M
            risk_score += 0.2
            risk_factors.append("very_small_cap")
        elif market_cap < 150_000_000:  # < $150M
            risk_score += 0.1
            risk_factors.append("small_micro_cap")
        
        # Price risk (penny stock)
        if price < 1.0:
            risk_score += 0.2
            risk_factors.append("sub_dollar_penny_stock")
        elif price < 5.0:
            risk_score += 0.1
            risk_factors.append("penny_stock")
        
        # Liquidity risk
        if avg_volume < 50_000:
            risk_score += 0.3
            risk_factors.append("very_low_liquidity")
        elif avg_volume < 200_000:
            risk_score += 0.2
            risk_factors.append("low_liquidity")
        elif avg_volume < 500_000:
            risk_score += 0.1
            risk_factors.append("moderate_liquidity")
        
        # Volatility risk
        if volatility > 1.0:  # >100% annualized
            risk_score += 0.2
            risk_factors.append("extreme_volatility")
        elif volatility > 0.6:  # >60% annualized
            risk_score += 0.15
            risk_factors.append("high_volatility")
        elif volatility > 0.4:
            risk_score += 0.1
            risk_factors.append("elevated_volatility")
        
        # Beta risk
        if abs(beta) > 2.0:
            risk_score += 0.1
            risk_factors.append("high_beta")
        
        # Normalize risk score
        risk_score = min(risk_score, 1.0)
        
        # Determine risk level (1-5)
        if risk_score >= 0.7:
            risk_level = 5
            overall_risk = "extreme"
        elif risk_score >= 0.5:
            risk_level = 4
            overall_risk = "high"
        elif risk_score >= 0.3:
            risk_level = 3
            overall_risk = "moderate"
        elif risk_score >= 0.15:
            risk_level = 2
            overall_risk = "low_moderate"
        else:
            risk_level = 1
            overall_risk = "low"
        
        risk_assessment['risk_score'] = risk_score
        risk_assessment['overall_risk'] = overall_risk
        risk_assessment['risk_level'] = risk_level
        risk_assessment['risk_factors'] = risk_factors
        
        return risk_assessment
    
    def calculate_kelly_criterion(self, win_rate: float, avg_win: float, 
                                  avg_loss: float) -> float:
        """
        Calculate Kelly Criterion for position sizing
        Returns fraction of portfolio to risk
        """
        if avg_loss == 0 or win_rate <= 0 or win_rate >= 1:
            return 0.0
        
        win_loss_ratio = avg_win / avg_loss
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        # Use fractional Kelly (25%) to be conservative
        fractional_kelly = kelly * 0.25
        
        # Cap at maximum position size
        return max(0.0, min(fractional_kelly, self.max_position_percent))
    
    def validate_entry(self, symbol: str, price: float, position: MicroCapPosition,
                      market_conditions: Dict) -> Tuple[bool, str]:
        """
        Validate if entry should be taken
        Returns (is_valid, reason)
        """
        # Check position size
        position_value = position.position_size * price
        if position_value > self.portfolio_value * self.max_position_percent * 2:
            return False, "position_too_large"
        
        # Check liquidity
        if position.liquidity_score < 0.3:
            return False, "insufficient_liquidity"
        
        # Check risk/reward
        if position.risk_reward_ratio < self.min_risk_reward:
            return False, "insufficient_risk_reward"
        
        # Check market conditions
        if market_conditions.get('market_regime') == 'bear_market':
            # More conservative in bear market
            if position.risk_reward_ratio < 3.0:
                return False, "insufficient_rr_for_bear_market"
        
        # Check gap risk (for penny stocks)
        if price < 5.0:
            # Ensure we can handle potential gaps
            max_loss_pct = position.max_loss_amount / self.portfolio_value
            if max_loss_pct > self.penny_max_position:
                return False, "excessive_gap_risk"
        
        return True, "validated"
    
    def calculate_portfolio_heat(self, open_positions: list) -> Dict:
        """
        Calculate total portfolio risk exposure
        """
        total_risk = 0.0
        total_value = 0.0
        
        for position in open_positions:
            total_risk += position.get('max_loss_amount', 0)
            total_value += position.get('position_value', 0)
        
        portfolio_heat = total_risk / self.portfolio_value if self.portfolio_value > 0 else 0
        
        return {
            'total_risk_amount': total_risk,
            'total_position_value': total_value,
            'portfolio_heat': portfolio_heat,
            'positions_count': len(open_positions),
            'heat_status': self._interpret_heat(portfolio_heat)
        }
    
    def _interpret_heat(self, heat: float) -> str:
        """Interpret portfolio heat level"""
        if heat >= self.max_portfolio_risk * 1.5:
            return "critical"
        elif heat >= self.max_portfolio_risk:
            return "high"
        elif heat >= self.max_portfolio_risk * 0.7:
            return "moderate"
        else:
            return "low"

# Example usage
if __name__ == "__main__":
    import config
    
    risk_mgr = MicroCapRiskManager(config, portfolio_value=100000)
    
    # Example micro-cap position calculation
    position = risk_mgr.calculate_position(
        symbol="MICR",
        entry_price=2.50,
        market_cap=50_000_000,
        avg_volume=250_000,
        volatility=0.65,
        is_penny=True
    )
    
    if position:
        print(f"Position: {position.position_size} shares")
        print(f"Stop Loss: ${position.stop_loss:.3f}")
        print(f"Take Profit: ${position.take_profit:.3f}")
        print(f"Risk/Reward: {position.risk_reward_ratio:.2f}:1")
        print(f"Liquidity Score: {position.liquidity_score:.2f}")

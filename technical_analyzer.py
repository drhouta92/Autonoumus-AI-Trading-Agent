"""
Technical analysis module for truly autonomous AI trading agent
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import talib

class TechnicalAnalyzer:
    def __init__(self, config):
        self.config = config
    
    def calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators for the given data
        """
        if data.empty or len(data) < 50:
            return data
        
        # Ensure data is sorted by date
        data = data.sort_index()
        
        close = data['Close'].values
        high = data['High'].values
        low = data['Low'].values
        volume = data['Volume'].values
        
        # Moving Averages
        data['SMA_10'] = talib.SMA(close, timeperiod=10)
        data['SMA_20'] = talib.SMA(close, timeperiod=20)
        data['SMA_50'] = talib.SMA(close, timeperiod=50)
        
        # RSI
        data['RSI'] = talib.RSI(close, timeperiod=14)
        
        # MACD
        macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        data['MACD'] = macd
        data['MACD_Signal'] = macd_signal
        data['MACD_Hist'] = macd_hist
        
        # Bollinger Bands
        upper, middle, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        data['BB_Upper'] = upper
        data['BB_Middle'] = middle
        data['BB_Lower'] = lower
        data['BB_Width'] = (upper - lower) / middle
        
        # Volume indicators
        data['Volume_SMA'] = talib.SMA(volume.astype(float), timeperiod=20)
        data['Volume_Ratio'] = volume.astype(float) / data['Volume_SMA']
        
        # Price patterns and trends
        data['Price_Change'] = data['Close'].pct_change()
        data['ATR'] = talib.ATR(high, low, close, timeperiod=14)
        
        return data
    
    def identify_trend(self, data: pd.DataFrame) -> str:
        """
        Identify the current trend based on moving averages
        """
        if data.empty or len(data) < 50:
            return 'Unknown'
        
        latest = data.iloc[-1]
        
        # Check if price is above moving averages
        if (not np.isnan(latest['SMA_10']) and not np.isnan(latest['SMA_20']) and 
            not np.isnan(latest['SMA_50']) and
            latest['Close'] > latest['SMA_10'] and 
            latest['Close'] > latest['SMA_20'] and 
            latest['Close'] > latest['SMA_50']):
            return 'Strong Bullish'
        elif (not np.isnan(latest['SMA_20']) and not np.isnan(latest['SMA_50']) and
              latest['Close'] > latest['SMA_20'] and 
              latest['Close'] > latest['SMA_50']):
            return 'Bullish'
        elif (not np.isnan(latest['SMA_20']) and not np.isnan(latest['SMA_50']) and
              latest['Close'] < latest['SMA_20'] and 
              latest['Close'] < latest['SMA_50']):
            return 'Bearish'
        else:
            return 'Neutral'
    
    def calculate_momentum_score(self, data: pd.DataFrame) -> float:
        """
        Calculate a momentum score based on multiple indicators
        """
        if data.empty or len(data) < 20:
            return 0.0
        
        latest = data.iloc[-1]
        score = 0.0
        
        # RSI contribution (0-30 points)
        if not np.isnan(latest['RSI']):
            if latest['RSI'] < 30:
                score += 15  # Oversold
            elif latest['RSI'] > 70:
                score -= 15  # Overbought
            else:
                # Linear score between 30-70
                score += (latest['RSI'] - 50) * 0.75
        
        # MACD contribution (0-20 points)
        if not np.isnan(latest['MACD_Hist']):
            if latest['MACD_Hist'] > 0:
                score += min(latest['MACD_Hist'] * 100, 20)
            else:
                score += max(latest['MACD_Hist'] * 100, -20)
        
        # Price trend contribution (0-20 points)
        if len(data) >= 20:
            price_trend_20d = (latest['Close'] / data['Close'].iloc[-20] - 1) * 100
            score += max(min(price_trend_20d * 0.5, 20), -20)
        
        # Volume contribution (0-15 points)
        if not np.isnan(latest['Volume_Ratio']):
            if latest['Volume_Ratio'] > 2:
                score += 15
            elif latest['Volume_Ratio'] > 1.5:
                score += 10
            elif latest['Volume_Ratio'] > 1:
                score += 5
        
        # Normalize to -1 to 1 range
        return max(min(score / 100, 1.0), -1.0)
    
    def detect_technical_patterns(self, data: pd.DataFrame) -> Dict:
        """
        Detect common technical patterns
        """
        if data.empty or len(data) < 30:
            return {}
        
        patterns = {}
        latest = data.iloc[-1]
        recent_data = data.tail(30)
        
        # Check for breakouts
        if not np.isnan(latest['BB_Upper']) and latest['Close'] > latest['BB_Upper']:
            patterns['bb_breakout'] = True
        elif not np.isnan(latest['BB_Lower']) and latest['Close'] < latest['BB_Lower']:
            patterns['bb_breakdown'] = True
        
        # Check for overbought/oversold conditions
        if not np.isnan(latest['RSI']):
            if latest['RSI'] > 70:
                patterns['rsi_overbought'] = True
            elif latest['RSI'] < 30:
                patterns['rsi_oversold'] = True
        
        # Check for MACD crossovers
        if len(data) >= 2:
            prev = data.iloc[-2]
            if (not np.isnan(latest['MACD']) and not np.isnan(latest['MACD_Signal']) and
                not np.isnan(prev['MACD']) and not np.isnan(prev['MACD_Signal'])):
                if prev['MACD'] <= prev['MACD_Signal'] and latest['MACD'] > latest['MACD_Signal']:
                    patterns['macd_bullish_crossover'] = True
                elif prev['MACD'] >= prev['MACD_Signal'] and latest['MACD'] < latest['MACD_Signal']:
                    patterns['macd_bearish_crossover'] = True
        
        return patterns

# Example usage
if __name__ == "__main__":
    pass
"""
Advanced Technical Analyzer
Specialized technical analysis for micro-cap and penny stocks
Includes volatility analysis and pattern recognition
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import talib

class AdvancedTechnicalAnalyzer:
    """
    Advanced technical analysis specialized for micro-cap stocks
    Handles high volatility and irregular patterns
    """
    
    def __init__(self, config):
        self.config = config
        self.min_data_points = 20  # Reduced for micro-caps
        
    def analyze_micro_cap(self, data: pd.DataFrame, symbol: str) -> Dict:
        """
        Comprehensive technical analysis for micro-cap stocks
        """
        if data.empty or len(data) < self.min_data_points:
            return self._empty_analysis()
        
        analysis = {}
        
        # Basic indicators
        analysis['indicators'] = self._calculate_indicators(data)
        
        # Volatility analysis (critical for micro-caps)
        analysis['volatility'] = self._analyze_volatility(data)
        
        # Pattern recognition
        analysis['patterns'] = self._detect_patterns(data)
        
        # Momentum analysis
        analysis['momentum'] = self._analyze_momentum(data)
        
        # Support/Resistance
        analysis['levels'] = self._find_support_resistance(data)
        
        # Volume analysis
        analysis['volume_analysis'] = self._analyze_volume(data)
        
        # Overall score
        analysis['technical_score'] = self._calculate_technical_score(analysis)
        
        return analysis
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis structure"""
        return {
            'indicators': {},
            'volatility': {},
            'patterns': [],
            'momentum': {},
            'levels': {},
            'volume_analysis': {},
            'technical_score': 0.0
        }
    
    def _calculate_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate technical indicators"""
        indicators = {}
        
        try:
            close = data['Close'].values
            high = data['High'].values
            low = data['Low'].values
            volume = data['Volume'].values
            
            # Moving averages
            if len(close) >= 10:
                indicators['sma_10'] = talib.SMA(close, timeperiod=10)[-1]
            if len(close) >= 20:
                indicators['sma_20'] = talib.SMA(close, timeperiod=20)[-1]
                indicators['ema_20'] = talib.EMA(close, timeperiod=20)[-1]
            
            # RSI (critical for overbought/oversold)
            if len(close) >= 14:
                rsi = talib.RSI(close, timeperiod=14)
                indicators['rsi'] = rsi[-1]
                indicators['rsi_signal'] = self._interpret_rsi(rsi[-1])
            
            # MACD
            if len(close) >= 26:
                macd, signal, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
                indicators['macd'] = macd[-1] if not np.isnan(macd[-1]) else 0
                indicators['macd_signal'] = signal[-1] if not np.isnan(signal[-1]) else 0
                indicators['macd_hist'] = hist[-1] if not np.isnan(hist[-1]) else 0
                indicators['macd_crossover'] = self._check_macd_crossover(macd, signal)
            
            # Bollinger Bands
            if len(close) >= 20:
                upper, middle, lower = talib.BBANDS(close, timeperiod=20)
                indicators['bb_upper'] = upper[-1]
                indicators['bb_middle'] = middle[-1]
                indicators['bb_lower'] = lower[-1]
                indicators['bb_width'] = (upper[-1] - lower[-1]) / middle[-1]
                indicators['bb_position'] = self._bb_position(close[-1], upper[-1], lower[-1])
            
            # Stochastic
            if len(close) >= 14:
                slowk, slowd = talib.STOCH(high, low, close, fastk_period=14, slowk_period=3, slowd_period=3)
                indicators['stoch_k'] = slowk[-1] if not np.isnan(slowk[-1]) else 50
                indicators['stoch_d'] = slowd[-1] if not np.isnan(slowd[-1]) else 50
                indicators['stoch_signal'] = self._interpret_stochastic(slowk[-1], slowd[-1])
            
            # ADX (trend strength)
            if len(close) >= 14:
                adx = talib.ADX(high, low, close, timeperiod=14)
                indicators['adx'] = adx[-1] if not np.isnan(adx[-1]) else 0
                indicators['trend_strength'] = self._interpret_adx(adx[-1] if not np.isnan(adx[-1]) else 0)
            
            # ATR (volatility)
            if len(close) >= 14:
                atr = talib.ATR(high, low, close, timeperiod=14)
                indicators['atr'] = atr[-1] if not np.isnan(atr[-1]) else 0
                indicators['atr_percent'] = (atr[-1] / close[-1]) * 100 if close[-1] > 0 else 0
            
        except Exception as e:
            print(f"Error calculating indicators: {e}")
        
        return indicators
    
    def _interpret_rsi(self, rsi: float) -> str:
        """Interpret RSI value"""
        if rsi >= 70:
            return "overbought"
        elif rsi <= 30:
            return "oversold"
        elif 45 <= rsi <= 55:
            return "neutral"
        elif rsi > 55:
            return "bullish"
        else:
            return "bearish"
    
    def _check_macd_crossover(self, macd: np.ndarray, signal: np.ndarray) -> str:
        """Check for MACD crossover"""
        if len(macd) < 2 or len(signal) < 2:
            return "none"
        
        if macd[-2] <= signal[-2] and macd[-1] > signal[-1]:
            return "bullish_crossover"
        elif macd[-2] >= signal[-2] and macd[-1] < signal[-1]:
            return "bearish_crossover"
        return "none"
    
    def _bb_position(self, price: float, upper: float, lower: float) -> str:
        """Determine position relative to Bollinger Bands"""
        if price >= upper:
            return "above_upper"
        elif price <= lower:
            return "below_lower"
        elif price > (upper + lower) / 2:
            return "upper_half"
        else:
            return "lower_half"
    
    def _interpret_stochastic(self, k: float, d: float) -> str:
        """Interpret Stochastic oscillator"""
        if k >= 80 and d >= 80:
            return "overbought"
        elif k <= 20 and d <= 20:
            return "oversold"
        elif k > d and k < 80:
            return "bullish"
        elif k < d and k > 20:
            return "bearish"
        return "neutral"
    
    def _interpret_adx(self, adx: float) -> str:
        """Interpret ADX trend strength"""
        if adx >= 50:
            return "very_strong"
        elif adx >= 25:
            return "strong"
        elif adx >= 20:
            return "moderate"
        else:
            return "weak"
    
    def _analyze_volatility(self, data: pd.DataFrame) -> Dict:
        """Analyze volatility metrics"""
        volatility = {}
        
        try:
            close = data['Close'].values
            high = data['High'].values
            low = data['Low'].values
            
            # Historical volatility
            returns = pd.Series(close).pct_change().dropna()
            volatility['historical_vol'] = returns.std() * np.sqrt(252)  # Annualized
            
            # Average True Range percentage
            if len(close) >= 14:
                atr = talib.ATR(high, low, close, timeperiod=14)
                volatility['atr_percent'] = (atr[-1] / close[-1]) * 100 if close[-1] > 0 else 0
            
            # Intraday range
            daily_ranges = (high - low) / close
            volatility['avg_daily_range'] = np.mean(daily_ranges[-10:]) * 100  # Last 10 days
            
            # Volatility classification
            if volatility['historical_vol'] > 1.0:  # >100%
                volatility['classification'] = "extreme"
            elif volatility['historical_vol'] > 0.6:  # >60%
                volatility['classification'] = "high"
            elif volatility['historical_vol'] > 0.3:  # >30%
                volatility['classification'] = "moderate"
            else:
                volatility['classification'] = "low"
            
        except Exception as e:
            print(f"Error analyzing volatility: {e}")
        
        return volatility
    
    def _detect_patterns(self, data: pd.DataFrame) -> List[str]:
        """Detect candlestick and chart patterns"""
        patterns = []
        
        try:
            open_prices = data['Open'].values
            high = data['High'].values
            low = data['Low'].values
            close = data['Close'].values
            
            if len(close) < 5:
                return patterns
            
            # Candlestick patterns
            if talib.CDLDOJI(open_prices, high, low, close)[-1] != 0:
                patterns.append("doji")
            
            if talib.CDLHAMMER(open_prices, high, low, close)[-1] != 0:
                patterns.append("hammer")
            
            if talib.CDLENGULFING(open_prices, high, low, close)[-1] > 0:
                patterns.append("bullish_engulfing")
            elif talib.CDLENGULFING(open_prices, high, low, close)[-1] < 0:
                patterns.append("bearish_engulfing")
            
            if talib.CDLMORNINGSTAR(open_prices, high, low, close)[-1] != 0:
                patterns.append("morning_star")
            
            if talib.CDLEVENINGSTAR(open_prices, high, low, close)[-1] != 0:
                patterns.append("evening_star")
            
            # Chart patterns (simple detection)
            if self._detect_breakout(data):
                patterns.append("breakout")
            
            if self._detect_consolidation(data):
                patterns.append("consolidation")
            
        except Exception as e:
            print(f"Error detecting patterns: {e}")
        
        return patterns
    
    def _detect_breakout(self, data: pd.DataFrame) -> bool:
        """Detect potential breakout pattern"""
        try:
            close = data['Close'].values
            if len(close) < 20:
                return False
            
            # Check if recent close breaks above recent high
            recent_high = np.max(close[-20:-1])
            if close[-1] > recent_high * 1.05:  # 5% above recent high
                return True
        except:
            pass
        return False
    
    def _detect_consolidation(self, data: pd.DataFrame) -> bool:
        """Detect consolidation pattern"""
        try:
            close = data['Close'].values
            if len(close) < 10:
                return False
            
            # Check if price is ranging (low volatility)
            recent_high = np.max(close[-10:])
            recent_low = np.min(close[-10:])
            range_percent = (recent_high - recent_low) / recent_low
            
            if range_percent < 0.10:  # Less than 10% range
                return True
        except:
            pass
        return False
    
    def _analyze_momentum(self, data: pd.DataFrame) -> Dict:
        """Analyze price momentum"""
        momentum = {}
        
        try:
            close = data['Close'].values
            
            # Price changes
            momentum['change_1d'] = (close[-1] / close[-2] - 1) if len(close) >= 2 else 0
            momentum['change_5d'] = (close[-1] / close[-6] - 1) if len(close) >= 6 else 0
            momentum['change_20d'] = (close[-1] / close[-21] - 1) if len(close) >= 21 else 0
            
            # Rate of change
            if len(close) >= 10:
                roc = talib.ROC(close, timeperiod=10)
                momentum['roc_10'] = roc[-1] if not np.isnan(roc[-1]) else 0
            
            # Money Flow Index (if volume available)
            if 'Volume' in data.columns and len(close) >= 14:
                mfi = talib.MFI(data['High'].values, data['Low'].values, 
                               close, data['Volume'].values, timeperiod=14)
                momentum['mfi'] = mfi[-1] if not np.isnan(mfi[-1]) else 50
            
            # Momentum classification
            if momentum['change_5d'] > 0.10:  # >10% gain
                momentum['classification'] = "strong_bullish"
            elif momentum['change_5d'] > 0.03:  # >3% gain
                momentum['classification'] = "bullish"
            elif momentum['change_5d'] < -0.10:  # >10% loss
                momentum['classification'] = "strong_bearish"
            elif momentum['change_5d'] < -0.03:  # >3% loss
                momentum['classification'] = "bearish"
            else:
                momentum['classification'] = "neutral"
            
        except Exception as e:
            print(f"Error analyzing momentum: {e}")
        
        return momentum
    
    def _find_support_resistance(self, data: pd.DataFrame) -> Dict:
        """Find support and resistance levels"""
        levels = {}
        
        try:
            close = data['Close'].values
            high = data['High'].values
            low = data['Low'].values
            
            if len(close) < 20:
                return levels
            
            # Recent support (lowest low in last 20 periods)
            levels['support'] = np.min(low[-20:])
            
            # Recent resistance (highest high in last 20 periods)
            levels['resistance'] = np.max(high[-20:])
            
            # Current position
            current = close[-1]
            range_size = levels['resistance'] - levels['support']
            if range_size > 0:
                position = (current - levels['support']) / range_size
                levels['position_in_range'] = position
                
                if position > 0.8:
                    levels['position_description'] = "near_resistance"
                elif position < 0.2:
                    levels['position_description'] = "near_support"
                else:
                    levels['position_description'] = "mid_range"
            
        except Exception as e:
            print(f"Error finding support/resistance: {e}")
        
        return levels
    
    def _analyze_volume(self, data: pd.DataFrame) -> Dict:
        """Analyze volume patterns"""
        volume_analysis = {}
        
        try:
            volume = data['Volume'].values
            close = data['Close'].values
            
            if len(volume) < 20:
                return volume_analysis
            
            # Volume metrics
            volume_analysis['current_volume'] = volume[-1]
            volume_analysis['avg_volume_20'] = np.mean(volume[-20:])
            volume_analysis['volume_ratio'] = volume[-1] / volume_analysis['avg_volume_20']
            
            # Volume trend
            recent_avg = np.mean(volume[-5:])
            older_avg = np.mean(volume[-20:-5])
            volume_analysis['volume_trend'] = "increasing" if recent_avg > older_avg else "decreasing"
            
            # On-Balance Volume
            if len(volume) >= 20:
                obv = talib.OBV(close, volume)
                volume_analysis['obv'] = obv[-1]
                volume_analysis['obv_trend'] = "bullish" if obv[-1] > obv[-10] else "bearish"
            
            # Volume spike detection
            if volume_analysis['volume_ratio'] > 3.0:
                volume_analysis['spike'] = "extreme"
            elif volume_analysis['volume_ratio'] > 2.0:
                volume_analysis['spike'] = "strong"
            elif volume_analysis['volume_ratio'] > 1.5:
                volume_analysis['spike'] = "moderate"
            else:
                volume_analysis['spike'] = "none"
            
        except Exception as e:
            print(f"Error analyzing volume: {e}")
        
        return volume_analysis
    
    def _calculate_technical_score(self, analysis: Dict) -> float:
        """Calculate overall technical score (0-1)"""
        score = 0.0
        weights = {
            'indicators': 0.30,
            'momentum': 0.25,
            'patterns': 0.20,
            'volume': 0.15,
            'volatility': 0.10
        }
        
        try:
            # Indicator score
            indicators = analysis.get('indicators', {})
            ind_score = 0.0
            if 'rsi_signal' in indicators:
                if indicators['rsi_signal'] in ['oversold', 'bullish']:
                    ind_score += 0.3
            if 'macd_crossover' in indicators:
                if indicators['macd_crossover'] == 'bullish_crossover':
                    ind_score += 0.4
            if 'stoch_signal' in indicators:
                if indicators['stoch_signal'] in ['oversold', 'bullish']:
                    ind_score += 0.3
            score += ind_score * weights['indicators']
            
            # Momentum score
            momentum = analysis.get('momentum', {})
            if momentum.get('classification') in ['strong_bullish', 'bullish']:
                score += weights['momentum']
            elif momentum.get('classification') in ['neutral']:
                score += weights['momentum'] * 0.5
            
            # Pattern score
            patterns = analysis.get('patterns', [])
            bullish_patterns = ['hammer', 'bullish_engulfing', 'morning_star', 'breakout']
            pattern_count = sum(1 for p in patterns if p in bullish_patterns)
            if pattern_count > 0:
                score += min(pattern_count * 0.5, 1.0) * weights['patterns']
            
            # Volume score
            volume = analysis.get('volume_analysis', {})
            if volume.get('spike') in ['extreme', 'strong']:
                score += weights['volume']
            elif volume.get('spike') == 'moderate':
                score += weights['volume'] * 0.5
            
            # Volatility bonus (micro-caps need volatility for opportunities)
            volatility = analysis.get('volatility', {})
            if volatility.get('classification') in ['high', 'moderate']:
                score += weights['volatility']
            
        except Exception as e:
            print(f"Error calculating technical score: {e}")
        
        return min(score, 1.0)

# Example usage
if __name__ == "__main__":
    import config
    import yfinance as yf
    
    analyzer = AdvancedTechnicalAnalyzer(config)
    ticker = yf.Ticker("AAPL")
    data = ticker.history(period="3mo")
    
    analysis = analyzer.analyze_micro_cap(data, "AAPL")
    print(f"Technical Score: {analysis['technical_score']:.3f}")
    print(f"Patterns detected: {analysis['patterns']}")

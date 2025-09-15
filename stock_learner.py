"""
Learning module for autonomous trading agent that remembers past discoveries
and learns from their performance over time.
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
import pickle
from typing import Dict, List, Set, Tuple

class StockLearner:
    def __init__(self, config):
        self.config = config
        self.historical_db_path = 'data/historical_stocks_db.csv'
        self.performance_db_path = 'data/performance_history.csv'
        self.model_path = 'models/scoring_weights.pkl'
        self.stock_universe = set()
        self.performance_history = pd.DataFrame()
        self.scoring_weights = {
            'momentum_weight': 0.25,
            'catalyst_weight': 0.20,
            'volume_weight': 0.15,
            'sentiment_weight': 0.15, 
            'trend_weight': 0.15,
            'pattern_weight': 0.10
        }
        
        # Create directories if they don't exist
        os.makedirs('data', exist_ok=True)
        os.makedirs('models', exist_ok=True)
        
        # Load historical data
        self._load_historical_data()
        self._load_scoring_weights()
    
    def _load_historical_data(self):
        """Load previously discovered stocks and their performance history"""
        try:
            if os.path.exists(self.historical_db_path):
                hist_df = pd.read_csv(self.historical_db_path)
                self.stock_universe = set(hist_df['symbol'].tolist())
                print(f"Loaded {len(self.stock_universe)} stocks from historical database")
            
            if os.path.exists(self.performance_db_path):
                self.performance_history = pd.read_csv(self.performance_db_path)
                print(f"Loaded {len(self.performance_history)} performance records")
        except Exception as e:
            print(f"Error loading historical data: {e}")
    
    def _load_scoring_weights(self):
        """Load previously optimized scoring weights"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.scoring_weights = pickle.load(f)
                print("Loaded optimized scoring weights from previous runs")
        except Exception as e:
            print(f"Error loading scoring weights: {e}")
    
    def get_combined_universe(self, new_discoveries: Set[str]) -> Set[str]:
        """Combine previously discovered stocks with new discoveries"""
        combined_universe = self.stock_universe.union(new_discoveries)
        print(f"Combined stock universe: {len(combined_universe)} symbols " 
              f"({len(self.stock_universe)} historical + {len(new_discoveries)} new)")
        return combined_universe
    
    def save_discoveries(self, symbols: Set[str], opportunities: List[Dict]):
        """Save newly discovered symbols and their evaluations"""
        try:
            # Update stock universe
            self.stock_universe = self.stock_universe.union(symbols)
            
            # Save symbols to CSV with timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d')
            
            # Create dataframe with all symbols and discovery date
            symbols_df = pd.DataFrame({
                'symbol': list(self.stock_universe),
                'last_discovery_date': timestamp
            })
            
            # If file exists, update last discovery date for new symbols
            if os.path.exists(self.historical_db_path):
                old_df = pd.read_csv(self.historical_db_path)
                # Merge keeping first discovery date from old data
                symbols_df = pd.merge(
                    symbols_df,
                    old_df[['symbol', 'first_discovery_date']],
                    on='symbol', how='left'
                )
                # Fill NaN first discovery dates with current date
                symbols_df['first_discovery_date'] = symbols_df['first_discovery_date'].fillna(timestamp)
            else:
                symbols_df['first_discovery_date'] = timestamp
            
            # Save to CSV
            symbols_df.to_csv(self.historical_db_path, index=False)
            print(f"Saved {len(self.stock_universe)} symbols to historical database")
            
            # Save opportunity details if available
            if opportunities:
                self._save_opportunity_data(opportunities)
        
        except Exception as e:
            print(f"Error saving discoveries: {e}")
    
    def _save_opportunity_data(self, opportunities: List[Dict]):
        """Save detailed opportunity evaluations"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d')
            opportunities_df = pd.DataFrame(opportunities)
            
            # Add evaluation timestamp
            opportunities_df['evaluation_date'] = timestamp
            
            # Add columns for future performance tracking
            opportunities_df['actual_performance_1d'] = None
            opportunities_df['actual_performance_1w'] = None
            opportunities_df['actual_performance_1m'] = None
            opportunities_df['prediction_accuracy'] = None
            
            # Append to existing file or create new one
            if os.path.exists(self.performance_db_path):
                old_performance = pd.read_csv(self.performance_db_path)
                combined_performance = pd.concat([old_performance, opportunities_df])
                combined_performance.to_csv(self.performance_db_path, index=False)
            else:
                opportunities_df.to_csv(self.performance_db_path, index=False)
            
            print(f"Saved {len(opportunities)} opportunity evaluations")
            
        except Exception as e:
            print(f"Error saving opportunity data: {e}")
    
    def update_performance_data(self, data_fetcher):
        """Update performance metrics for past predictions"""
        try:
            if not os.path.exists(self.performance_db_path):
                print("No performance history found to update")
                return
            
            performance_df = pd.read_csv(self.performance_db_path)
            
            # Find records with missing performance data
            missing_data = performance_df[
                (performance_df['actual_performance_1m'].isnull()) & 
                (pd.to_datetime(performance_df['evaluation_date']) < 
                 datetime.now() - timedelta(days=30))
            ]
            
            if missing_data.empty:
                print("No performance data needs updating")
                return
            
            print(f"Updating performance data for {len(missing_data)} past predictions")
            
            for idx, row in missing_data.iterrows():
                symbol = row['symbol']
                eval_date = pd.to_datetime(row['evaluation_date'])
                
                # Get historical data since evaluation date
                hist_data = data_fetcher.get_historical_data(symbol, '3mo')
                
                if hist_data.empty:
                    continue
                
                # Find closest date in historical data to evaluation date
                hist_data.reset_index(inplace=True)
                if 'Date' not in hist_data.columns:
                    continue
                    
                hist_data['Date'] = pd.to_datetime(hist_data['Date'])
                closest_date_idx = (hist_data['Date'] - eval_date).abs().idxmin()
                
                # Get start price and prices after 1d, 1w, 1m
                try:
                    start_price = hist_data.loc[closest_date_idx, 'Close']
                    
                    # 1 day performance
                    if closest_date_idx + 1 < len(hist_data):
                        price_1d = hist_data.loc[closest_date_idx + 1, 'Close']
                        perf_1d = (price_1d - start_price) / start_price * 100
                        performance_df.loc[idx, 'actual_performance_1d'] = perf_1d
                    
                    # 1 week performance (approx 5 trading days)
                    if closest_date_idx + 5 < len(hist_data):
                        price_1w = hist_data.loc[closest_date_idx + 5, 'Close']
                        perf_1w = (price_1w - start_price) / start_price * 100
                        performance_df.loc[idx, 'actual_performance_1w'] = perf_1w
                    
                    # 1 month performance (approx 21 trading days)
                    if closest_date_idx + 21 < len(hist_data):
                        price_1m = hist_data.loc[closest_date_idx + 21, 'Close']
                        perf_1m = (price_1m - start_price) / start_price * 100
                        performance_df.loc[idx, 'actual_performance_1m'] = perf_1m
                    
                    # Calculate prediction accuracy
                    # Simple version: if overall_score > 0.5, we expect positive performance
                    if not pd.isnull(performance_df.loc[idx, 'actual_performance_1m']):
                        expected_positive = row['overall_score'] > 0.5
                        actual_positive = performance_df.loc[idx, 'actual_performance_1m'] > 0
                        accuracy = 1.0 if expected_positive == actual_positive else 0.0
                        performance_df.loc[idx, 'prediction_accuracy'] = accuracy
                
                except Exception as e:
                    print(f"Error calculating performance for {symbol}: {e}")
            
            # Save updated data
            performance_df.to_csv(self.performance_db_path, index=False)
            self.performance_history = performance_df
            print(f"Updated performance data for {len(missing_data)} predictions")
            
            # Learn from updated performance data
            self._optimize_scoring_weights()
            
        except Exception as e:
            print(f"Error updating performance data: {e}")
    
    def _optimize_scoring_weights(self):
        """Optimize scoring weights based on prediction accuracy"""
        try:
            if self.performance_history.empty:
                return
            
            # Get only rows with complete performance data
            complete_data = self.performance_history.dropna(subset=['actual_performance_1m', 'prediction_accuracy'])
            
            if len(complete_data) < 30:  # Need enough data to optimize weights
                print("Not enough historical data for weight optimization")
                return
            
            print("Optimizing scoring weights based on historical performance...")
            
            # Simple reinforcement learning approach
            # Calculate correlation between features and actual performance
            correlations = {}
            features = [
                'momentum_score', 'catalyst_score', 'sentiment_score',
                'buzz_score', 'volume_ratio'
            ]
            
            for feature in features:
                if feature in complete_data.columns:
                    corr = complete_data[feature].corr(complete_data['actual_performance_1m'])
                    if pd.notnull(corr):
                        correlations[feature] = abs(corr)  # Use absolute correlation
            
            if not correlations:
                return
                
            # Normalize correlations to sum to 1
            total_corr = sum(correlations.values())
            if total_corr > 0:
                normalized_weights = {k: v/total_corr for k, v in correlations.items()}
                
                # Update weights based on correlations
                if 'momentum_score' in normalized_weights:
                    self.scoring_weights['momentum_weight'] = normalized_weights['momentum_score'] * 0.8 + self.scoring_weights['momentum_weight'] * 0.2
                
                if 'catalyst_score' in normalized_weights:
                    self.scoring_weights['catalyst_weight'] = normalized_weights['catalyst_score'] * 0.8 + self.scoring_weights['catalyst_weight'] * 0.2
                    
                if 'sentiment_score' in normalized_weights:
                    self.scoring_weights['sentiment_weight'] = normalized_weights['sentiment_score'] * 0.8 + self.scoring_weights['sentiment_weight'] * 0.2
                    
                if 'volume_ratio' in normalized_weights:
                    self.scoring_weights['volume_weight'] = normalized_weights['volume_ratio'] * 0.8 + self.scoring_weights['volume_weight'] * 0.2
                
                # Normalize weights to sum to 1
                total_weight = sum(self.scoring_weights.values())
                self.scoring_weights = {k: v/total_weight for k, v in self.scoring_weights.items()}
                
                # Save optimized weights
                with open(self.model_path, 'wb') as f:
                    pickle.dump(self.scoring_weights, f)
                
                print("Scoring weights optimized based on historical performance")
                print("New weights:", self.scoring_weights)
        
        except Exception as e:
            print(f"Error optimizing scoring weights: {e}")
    
    def get_top_historical_performers(self, limit=20) -> List[str]:
        """Get top historical performing stocks"""
        try:
            if self.performance_history.empty:
                return []
            
            # Filter stocks with performance data
            performers = self.performance_history.dropna(subset=['actual_performance_1m'])
            
            if performers.empty:
                return []
                
            # Group by symbol and calculate average performance
            avg_performance = performers.groupby('symbol')['actual_performance_1m'].mean().reset_index()
            
            # Sort by performance and get top performers
            top_performers = avg_performance.sort_values('actual_performance_1m', ascending=False)
            
            return top_performers.head(limit)['symbol'].tolist()
            
        except Exception as e:
            print(f"Error getting top performers: {e}")
            return []
    
    def calculate_learning_adjusted_score(self, opportunity: Dict) -> float:
        """Calculate opportunity score adjusted by learning weights"""
        try:
            if not opportunity:
                return 0.0
                
            # Apply learned weights to scoring components
            adjusted_score = (
                opportunity.get('momentum_score', 0) * self.scoring_weights['momentum_weight'] +
                opportunity.get('catalyst_score', 0) * self.scoring_weights['catalyst_weight'] +
                opportunity.get('volume_ratio', 1) / 5 * self.scoring_weights['volume_weight'] +
                opportunity.get('sentiment_score', 0) * self.scoring_weights['sentiment_weight'] +
                (len(opportunity.get('technical_patterns', [])) / 10) * self.scoring_weights['pattern_weight']
            )
            
            # Add bonus for stocks that performed well historically
            if not self.performance_history.empty:
                symbol = opportunity.get('symbol')
                if symbol in self.performance_history['symbol'].values:
                    hist_perf = self.performance_history[self.performance_history['symbol'] == symbol]['actual_performance_1m'].mean()
                    if not pd.isnull(hist_perf) and hist_perf > 0:
                        adjusted_score *= (1 + min(hist_perf/100, 0.5))  # Up to 50% boost for good performers
            
            return min(adjusted_score, 1.0)
            
        except Exception as e:
            print(f"Error calculating learning adjusted score: {e}")
            return 0.0
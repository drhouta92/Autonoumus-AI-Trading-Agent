"""
Brain Manager - Kill-Gate Evolution System
Manages agent brain state with single-file JSON, auto-rotation, and SQLite hot-switching
"""

import json
import sqlite3
import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading
import time

@dataclass
class BrainState:
    """Single brain state snapshot"""
    timestamp: str
    generation: int
    performance_score: float
    discovery_weights: Dict[str, float]
    scoring_weights: Dict[str, float]
    threshold_values: Dict[str, float]
    learned_patterns: Dict[str, Any]
    decision_history: List[Dict]
    kill_gate_status: str  # "alive", "zombie", "killed"
    
class BrainManager:
    """
    Manages AI agent brain with kill-gate evolution mechanism
    - Single-file JSON state for fast access
    - Auto-rotation to SQLite for historical data
    - Hot-switch capability between JSON and SQLite
    - Offline learning and evolution tracking
    """
    
    def __init__(self, config, brain_file="brain_state.json", 
                 db_file="brain_history.db", max_json_generations=100):
        self.config = config
        self.brain_file = brain_file
        self.db_file = db_file
        self.max_json_generations = max_json_generations
        
        # Current brain state
        self.current_brain: Optional[BrainState] = None
        self.generation = 0
        self.performance_threshold = 0.5  # Kill-gate threshold
        self.zombie_grace_period = 5  # Generations before kill
        self.zombie_counter = 0
        
        # Threading for auto-rotation
        self.auto_save_interval = 300  # 5 minutes
        self.save_thread = None
        self.running = False
        
        # Initialize
        self._initialize_brain()
        self._initialize_database()
        
    def _initialize_brain(self):
        """Initialize or load brain state"""
        if os.path.exists(self.brain_file):
            self._load_brain()
            print(f"🧠 Loaded brain generation {self.generation}")
        else:
            self._create_new_brain()
            print(f"🧠 Created new brain generation {self.generation}")
    
    def _create_new_brain(self):
        """Create a fresh brain with default parameters"""
        self.current_brain = BrainState(
            timestamp=datetime.now().isoformat(),
            generation=self.generation,
            performance_score=0.0,
            discovery_weights={
                'indices': 1.0,
                'etfs': 1.0,
                'news': 1.2,
                'sectors': 1.0,
                'trending': 1.3,
                'websites': 1.1,
                'micro_cap_screeners': 1.5,
                'penny_stock_sources': 1.4
            },
            scoring_weights={
                'momentum': 0.25,
                'catalyst': 0.20,
                'volume': 0.15,
                'sentiment': 0.15,
                'micro_cap_risk': 0.15,
                'technical_pattern': 0.10
            },
            threshold_values={
                'min_confidence': 0.7,
                'min_volume_ratio': 2.0,
                'min_momentum_score': 0.6,
                'max_micro_cap': 300_000_000,  # $300M
                'min_liquidity': 50000
            },
            learned_patterns={
                'successful_sectors': [],
                'successful_patterns': [],
                'failed_symbols': [],
                'optimal_entry_times': []
            },
            decision_history=[],
            kill_gate_status="alive"
        )
        self._save_brain()
    
    def _load_brain(self):
        """Load brain state from JSON file"""
        try:
            with open(self.brain_file, 'r') as f:
                data = json.load(f)
                self.current_brain = BrainState(**data)
                self.generation = self.current_brain.generation
                print(f"Brain status: {self.current_brain.kill_gate_status}")
        except Exception as e:
            print(f"Error loading brain: {e}, creating new brain")
            self._create_new_brain()
    
    def _save_brain(self):
        """Save current brain state to JSON file"""
        try:
            with open(self.brain_file, 'w') as f:
                json.dump(asdict(self.current_brain), f, indent=2)
        except Exception as e:
            print(f"Error saving brain: {e}")
    
    def _initialize_database(self):
        """Initialize SQLite database for historical brain states"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS brain_generations (
                    generation INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    performance_score REAL,
                    kill_gate_status TEXT,
                    discovery_weights TEXT,
                    scoring_weights TEXT,
                    threshold_values TEXT,
                    learned_patterns TEXT,
                    decision_count INTEGER
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    generation INTEGER,
                    timestamp TEXT,
                    symbol TEXT,
                    action TEXT,
                    confidence REAL,
                    outcome TEXT,
                    FOREIGN KEY (generation) REFERENCES brain_generations (generation)
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    def evolve_brain(self, performance_score: float, learning_data: Dict):
        """
        Kill-gate evolution mechanism
        - Evaluate performance against threshold
        - Mark as zombie if underperforming
        - Kill and rebirth if zombie too long
        - Evolve weights based on learning data
        """
        self.generation += 1
        self.current_brain.generation = self.generation
        self.current_brain.timestamp = datetime.now().isoformat()
        self.current_brain.performance_score = performance_score
        
        # Kill-gate logic
        if performance_score < self.performance_threshold:
            if self.current_brain.kill_gate_status == "alive":
                self.current_brain.kill_gate_status = "zombie"
                self.zombie_counter = 1
                print(f"⚠️  Brain marked as ZOMBIE (performance: {performance_score:.3f})")
            elif self.current_brain.kill_gate_status == "zombie":
                self.zombie_counter += 1
                if self.zombie_counter >= self.zombie_grace_period:
                    print(f"💀 Brain KILLED after {self.zombie_counter} zombie generations")
                    self._kill_and_rebirth()
                    return
                else:
                    print(f"⚠️  Brain still ZOMBIE ({self.zombie_counter}/{self.zombie_grace_period})")
        else:
            if self.current_brain.kill_gate_status in ["zombie", "killed"]:
                print(f"✅ Brain RESURRECTED (performance: {performance_score:.3f})")
            self.current_brain.kill_gate_status = "alive"
            self.zombie_counter = 0
        
        # Evolve weights based on learning data
        self._apply_learning(learning_data)
        
        # Save and rotate if needed
        self._save_brain()
        self._check_rotation()
    
    def _kill_and_rebirth(self):
        """Kill current brain and create new one with randomized parameters"""
        # Archive current brain to database
        self._archive_to_database()
        
        # Create new brain with randomized weights
        old_weights = self.current_brain.discovery_weights.copy()
        self._create_new_brain()
        
        # Randomize weights within reasonable bounds
        for key in self.current_brain.discovery_weights:
            if key in old_weights:
                # Mutate old weight by ±30%
                mutation = 1.0 + (random.uniform(-0.3, 0.3))
                self.current_brain.discovery_weights[key] = max(0.5, min(2.0, old_weights[key] * mutation))
        
        print(f"🔄 Brain REBORN as generation {self.generation}")
        self.current_brain.kill_gate_status = "alive"
    
    def _apply_learning(self, learning_data: Dict):
        """Apply learned patterns to brain state"""
        if 'successful_sectors' in learning_data:
            self.current_brain.learned_patterns['successful_sectors'].extend(
                learning_data['successful_sectors']
            )
            # Keep only top 10
            self.current_brain.learned_patterns['successful_sectors'] = \
                self.current_brain.learned_patterns['successful_sectors'][-10:]
        
        if 'weight_adjustments' in learning_data:
            for key, adjustment in learning_data['weight_adjustments'].items():
                if key in self.current_brain.scoring_weights:
                    self.current_brain.scoring_weights[key] *= (1 + adjustment)
                    # Normalize
                    total = sum(self.current_brain.scoring_weights.values())
                    for k in self.current_brain.scoring_weights:
                        self.current_brain.scoring_weights[k] /= total
    
    def _check_rotation(self):
        """Check if JSON file needs rotation to SQLite"""
        if self.generation % self.max_json_generations == 0:
            print(f"🔄 Rotating brain to SQLite (generation {self.generation})")
            self._archive_to_database()
    
    def _archive_to_database(self):
        """Archive current brain state to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO brain_generations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.current_brain.generation,
                self.current_brain.timestamp,
                self.current_brain.performance_score,
                self.current_brain.kill_gate_status,
                json.dumps(self.current_brain.discovery_weights),
                json.dumps(self.current_brain.scoring_weights),
                json.dumps(self.current_brain.threshold_values),
                json.dumps(self.current_brain.learned_patterns),
                len(self.current_brain.decision_history)
            ))
            
            # Archive decisions
            for decision in self.current_brain.decision_history:
                cursor.execute('''
                    INSERT INTO decisions (generation, timestamp, symbol, action, confidence, outcome)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    self.current_brain.generation,
                    decision.get('timestamp'),
                    decision.get('symbol'),
                    decision.get('action'),
                    decision.get('confidence'),
                    decision.get('outcome', 'pending')
                ))
            
            conn.commit()
            conn.close()
            
            # Clear old decision history from JSON
            self.current_brain.decision_history = []
            
        except Exception as e:
            print(f"Error archiving to database: {e}")
    
    def hot_switch_to_sqlite(self):
        """Hot-switch: move all data to SQLite and use only database"""
        print("🔥 Hot-switching to SQLite mode...")
        self._archive_to_database()
        
        # Backup JSON file
        if os.path.exists(self.brain_file):
            backup_file = f"{self.brain_file}.backup"
            shutil.copy(self.brain_file, backup_file)
            print(f"📁 JSON backed up to {backup_file}")
    
    def load_from_sqlite(self, generation: int) -> Optional[BrainState]:
        """Load a specific generation from SQLite"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM brain_generations WHERE generation = ?
            ''', (generation,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return BrainState(
                    timestamp=row[1],
                    generation=row[0],
                    performance_score=row[2],
                    discovery_weights=json.loads(row[4]),
                    scoring_weights=json.loads(row[5]),
                    threshold_values=json.loads(row[6]),
                    learned_patterns=json.loads(row[7]),
                    decision_history=[],
                    kill_gate_status=row[3]
                )
            return None
        except Exception as e:
            print(f"Error loading from SQLite: {e}")
            return None
    
    def get_brain_statistics(self) -> Dict:
        """Get statistics about brain evolution"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM brain_generations')
            total_generations = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT AVG(performance_score), MAX(performance_score), MIN(performance_score)
                FROM brain_generations
            ''')
            avg_perf, max_perf, min_perf = cursor.fetchone()
            
            cursor.execute('''
                SELECT kill_gate_status, COUNT(*) FROM brain_generations
                GROUP BY kill_gate_status
            ''')
            status_counts = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'current_generation': self.generation,
                'total_archived': total_generations,
                'current_status': self.current_brain.kill_gate_status,
                'current_performance': self.current_brain.performance_score,
                'avg_performance': avg_perf or 0.0,
                'max_performance': max_perf or 0.0,
                'min_performance': min_perf or 0.0,
                'status_distribution': status_counts
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def record_decision(self, symbol: str, action: str, confidence: float):
        """Record a trading decision"""
        decision = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'action': action,
            'confidence': confidence,
            'outcome': 'pending'
        }
        self.current_brain.decision_history.append(decision)
    
    def start_auto_save(self):
        """Start background thread for auto-saving brain state"""
        if not self.running:
            self.running = True
            self.save_thread = threading.Thread(target=self._auto_save_loop, daemon=True)
            self.save_thread.start()
            print("🔄 Auto-save thread started")
    
    def stop_auto_save(self):
        """Stop auto-save thread"""
        self.running = False
        if self.save_thread:
            self.save_thread.join(timeout=5)
            print("⏹️  Auto-save thread stopped")
    
    def _auto_save_loop(self):
        """Background loop for auto-saving"""
        while self.running:
            time.sleep(self.auto_save_interval)
            if self.current_brain:
                self._save_brain()
                print(f"💾 Auto-saved brain (generation {self.generation})")

import random

# Example usage
if __name__ == "__main__":
    import config
    brain = BrainManager(config)
    print(brain.get_brain_statistics())

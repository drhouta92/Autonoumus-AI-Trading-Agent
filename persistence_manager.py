"""
Persistence Manager
Handles data persistence with hot-switching between JSON and SQLite
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd

class PersistenceManager:
    """
    Manages data persistence with dual storage:
    - JSON for fast access and recent data
    - SQLite for historical data and hot-switch capability
    """
    
    def __init__(self, config, json_dir="data/json", db_file="data/trading.db"):
        self.config = config
        self.json_dir = json_dir
        self.db_file = db_file
        
        # Create directories
        os.makedirs(json_dir, exist_ok=True)
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database with tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Opportunities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                price REAL,
                market_cap REAL,
                overall_score REAL,
                momentum_score REAL,
                catalyst_score REAL,
                technical_score REAL,
                is_penny_stock INTEGER,
                is_micro_cap INTEGER,
                sector TEXT,
                exchange TEXT
            )
        ''')
        
        # Decisions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                action TEXT,
                confidence REAL,
                reasons TEXT,
                score_breakdown TEXT,
                risk_assessment TEXT
            )
        ''')
        
        # Positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                entry_date TEXT,
                exit_date TEXT,
                entry_price REAL,
                exit_price REAL,
                position_size INTEGER,
                stop_loss REAL,
                take_profit REAL,
                profit_loss REAL,
                status TEXT
            )
        ''')
        
        # Performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_opportunities INTEGER,
                decisions_made INTEGER,
                buy_signals INTEGER,
                avg_confidence REAL,
                brain_generation INTEGER,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_opportunity(self, opportunity: Dict, use_json: bool = True):
        """Save opportunity to storage"""
        if use_json:
            self._save_opportunity_json(opportunity)
        else:
            self._save_opportunity_db(opportunity)
    
    def _save_opportunity_json(self, opportunity: Dict):
        """Save opportunity to JSON file"""
        filename = f"{self.json_dir}/opportunities_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Load existing data
        opportunities = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                opportunities = json.load(f)
        
        # Add timestamp
        opportunity['saved_at'] = datetime.now().isoformat()
        opportunities.append(opportunity)
        
        # Save
        with open(filename, 'w') as f:
            json.dump(opportunities, f, indent=2)
    
    def _save_opportunity_db(self, opportunity: Dict):
        """Save opportunity to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO opportunities 
            (symbol, timestamp, price, market_cap, overall_score, momentum_score,
             catalyst_score, technical_score, is_penny_stock, is_micro_cap,
             sector, exchange)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            opportunity.get('symbol'),
            datetime.now().isoformat(),
            opportunity.get('price'),
            opportunity.get('market_cap'),
            opportunity.get('overall_score'),
            opportunity.get('momentum_score'),
            opportunity.get('catalyst_score'),
            opportunity.get('technical_score'),
            1 if opportunity.get('is_penny_stock') else 0,
            1 if opportunity.get('is_micro_cap') else 0,
            opportunity.get('sector'),
            opportunity.get('exchange')
        ))
        
        conn.commit()
        conn.close()
    
    def save_decision(self, decision, use_json: bool = True):
        """Save trading decision"""
        if use_json:
            self._save_decision_json(decision)
        else:
            self._save_decision_db(decision)
    
    def _save_decision_json(self, decision):
        """Save decision to JSON file"""
        filename = f"{self.json_dir}/decisions_{datetime.now().strftime('%Y%m%d')}.json"
        
        decisions = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                decisions = json.load(f)
        
        decision_dict = {
            'symbol': decision.symbol,
            'timestamp': decision.timestamp,
            'action': decision.action,
            'confidence': decision.confidence,
            'reasons': decision.reasons,
            'score_breakdown': decision.score_breakdown,
            'risk_assessment': decision.risk_assessment
        }
        
        decisions.append(decision_dict)
        
        with open(filename, 'w') as f:
            json.dump(decisions, f, indent=2)
    
    def _save_decision_db(self, decision):
        """Save decision to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO decisions 
            (symbol, timestamp, action, confidence, reasons, score_breakdown, risk_assessment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            decision.symbol,
            decision.timestamp,
            decision.action,
            decision.confidence,
            json.dumps(decision.reasons),
            json.dumps(decision.score_breakdown),
            json.dumps(decision.risk_assessment)
        ))
        
        conn.commit()
        conn.close()
    
    def load_opportunities(self, days: int = 7) -> List[Dict]:
        """Load recent opportunities"""
        opportunities = []
        
        # Try JSON files first
        for i in range(days):
            date = datetime.now() - pd.Timedelta(days=i)
            filename = f"{self.json_dir}/opportunities_{date.strftime('%Y%m%d')}.json"
            
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    opportunities.extend(json.load(f))
        
        return opportunities
    
    def load_decisions(self, days: int = 7) -> List[Dict]:
        """Load recent decisions"""
        decisions = []
        
        for i in range(days):
            date = datetime.now() - pd.Timedelta(days=i)
            filename = f"{self.json_dir}/decisions_{date.strftime('%Y%m%d')}.json"
            
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    decisions.extend(json.load(f))
        
        return decisions
    
    def migrate_to_sqlite(self, days_to_keep_json: int = 7):
        """
        Migrate old JSON data to SQLite
        Keep only recent data in JSON
        """
        print(f"🔄 Migrating data to SQLite...")
        
        # Find all JSON files
        opportunity_files = [f for f in os.listdir(self.json_dir) 
                           if f.startswith('opportunities_') and f.endswith('.json')]
        decision_files = [f for f in os.listdir(self.json_dir)
                         if f.startswith('decisions_') and f.endswith('.json')]
        
        migrated_count = 0
        
        # Migrate opportunities
        for filename in opportunity_files:
            filepath = os.path.join(self.json_dir, filename)
            
            # Check file age
            file_date = datetime.fromtimestamp(os.path.getmtime(filepath))
            age_days = (datetime.now() - file_date).days
            
            if age_days > days_to_keep_json:
                with open(filepath, 'r') as f:
                    opportunities = json.load(f)
                
                # Save to database
                for opp in opportunities:
                    self._save_opportunity_db(opp)
                    migrated_count += 1
                
                # Delete JSON file
                os.remove(filepath)
                print(f"  Migrated and deleted: {filename}")
        
        # Migrate decisions
        for filename in decision_files:
            filepath = os.path.join(self.json_dir, filename)
            
            file_date = datetime.fromtimestamp(os.path.getmtime(filepath))
            age_days = (datetime.now() - file_date).days
            
            if age_days > days_to_keep_json:
                with open(filepath, 'r') as f:
                    decisions = json.load(f)
                
                # Save to database
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                for dec in decisions:
                    cursor.execute('''
                        INSERT INTO decisions 
                        (symbol, timestamp, action, confidence, reasons, score_breakdown, risk_assessment)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        dec.get('symbol'),
                        dec.get('timestamp'),
                        dec.get('action'),
                        dec.get('confidence'),
                        json.dumps(dec.get('reasons', [])),
                        json.dumps(dec.get('score_breakdown', {})),
                        json.dumps(dec.get('risk_assessment', {}))
                    ))
                    migrated_count += 1
                
                conn.commit()
                conn.close()
                
                os.remove(filepath)
                print(f"  Migrated and deleted: {filename}")
        
        print(f"✅ Migrated {migrated_count} records to SQLite")
    
    def get_statistics(self) -> Dict:
        """Get storage statistics"""
        stats = {
            'json_files': 0,
            'db_records': 0,
            'total_opportunities': 0,
            'total_decisions': 0
        }
        
        # Count JSON files
        if os.path.exists(self.json_dir):
            stats['json_files'] = len([f for f in os.listdir(self.json_dir) if f.endswith('.json')])
        
        # Count database records
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM opportunities')
            stats['total_opportunities'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM decisions')
            stats['total_decisions'] = cursor.fetchone()[0]
            
            stats['db_records'] = stats['total_opportunities'] + stats['total_decisions']
            
            conn.close()
        except Exception as e:
            print(f"Error getting database stats: {e}")
        
        return stats
    
    def export_to_csv(self, output_dir: str = "exports"):
        """Export data to CSV files"""
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            conn = sqlite3.connect(self.db_file)
            
            # Export opportunities
            df_opp = pd.read_sql_query('SELECT * FROM opportunities', conn)
            df_opp.to_csv(f"{output_dir}/opportunities.csv", index=False)
            
            # Export decisions
            df_dec = pd.read_sql_query('SELECT * FROM decisions', conn)
            df_dec.to_csv(f"{output_dir}/decisions.csv", index=False)
            
            # Export performance
            df_perf = pd.read_sql_query('SELECT * FROM performance', conn)
            df_perf.to_csv(f"{output_dir}/performance.csv", index=False)
            
            conn.close()
            
            print(f"✅ Exported data to {output_dir}/")
        except Exception as e:
            print(f"Error exporting to CSV: {e}")

# Example usage
if __name__ == "__main__":
    import config
    
    pm = PersistenceManager(config)
    print(pm.get_statistics())

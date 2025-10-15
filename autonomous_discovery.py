import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Set
import time
import random
import os
import json
import threading
from data_fetcher import DataFetcher
from technical_analyzer import TechnicalAnalyzer
from catalyst_detector import CatalystDetector
from risk_manager import RiskManager


class ProgressTracker:
    """
    Track symbol progression through evaluation gates with pass/fail statistics
    """
    def __init__(self):
        self.gates = {
            'G1': {'name': 'Symbol Discovery', 'total': 0, 'passed': 0, 'failed': 0},
            'G2': {'name': 'Fundamental Data', 'total': 0, 'passed': 0, 'failed': 0},
            'G3': {'name': 'Price Validation', 'total': 0, 'passed': 0, 'failed': 0},
            'G4': {'name': 'Historical Data', 'total': 0, 'passed': 0, 'failed': 0},
            'G5': {'name': 'Technical Analysis', 'total': 0, 'passed': 0, 'failed': 0},
            'G6': {'name': 'Catalyst Analysis', 'total': 0, 'passed': 0, 'failed': 0},
            'G7': {'name': 'Volume Analysis', 'total': 0, 'passed': 0, 'failed': 0},
            'G8': {'name': 'Score Calculation', 'total': 0, 'passed': 0, 'failed': 0},
            'G9': {'name': 'Risk Assessment', 'total': 0, 'passed': 0, 'failed': 0},
            'G10': {'name': 'Final Position', 'total': 0, 'passed': 0, 'failed': 0},
        }
        self.lock = threading.Lock()
    
    def record_gate(self, gate_id: str, passed: bool):
        """Record a symbol's result at a gate"""
        with self.lock:
            if gate_id in self.gates:
                self.gates[gate_id]['total'] += 1
                if passed:
                    self.gates[gate_id]['passed'] += 1
                else:
                    self.gates[gate_id]['failed'] += 1
    
    def render_progress_bars(self):
        """Render progress bars showing gate statistics"""
        print("\n" + "="*80)
        print("EVALUATION PIPELINE PROGRESS")
        print("="*80)
        
        for gate_id in sorted(self.gates.keys()):
            gate = self.gates[gate_id]
            name = gate['name']
            total = gate['total']
            passed = gate['passed']
            failed = gate['failed']
            
            if total == 0:
                # No symbols have reached this gate yet
                print(f"{gate_id} {name:20s} | 0.0% waiting...")
            else:
                pass_rate = (passed / total * 100) if total > 0 else 0
                fail_rate = (failed / total * 100) if total > 0 else 0
                
                # Create visual bar
                bar_length = 40
                passed_bar = int(pass_rate / 100 * bar_length)
                failed_bar = int(fail_rate / 100 * bar_length)
                remaining_bar = bar_length - passed_bar - failed_bar
                
                bar = '█' * passed_bar + '▓' * failed_bar + '░' * remaining_bar
                
                print(f"{gate_id} {name:20s} | {bar} | " +
                      f"Total: {total:4d} Pass: {passed:4d} ({pass_rate:5.1f}%) " +
                      f"Fail: {failed:4d} ({fail_rate:5.1f}%)")
        
        print("="*80 + "\n")

class AutonomousDiscovery:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.discovery_weights = {
            'indices': 1.0,
            'etfs': 1.0,
            'news': 1.0,
            'sectors': 1.0,
            'trending': 1.0,
            'websites': 1.0
        }
        self.historical_data_path = "historical_stocks.json"
        self.performance_history_path = "stock_performance.json"
        self.progress_tracker = ProgressTracker()
        
    def discover_symbols_from_scratch(self) -> Set[str]:
        """
        Discover stock symbols from absolute scratch - no predefined lists
        Also incorporates learning from previously discovered symbols
        """
        print("=== TRULY AUTONOMOUS SYMBOL DISCOVERY WITH LEARNING ===")
        print("Building stock universe from scratch and historical learning...")
        all_symbols = set()
        
        # Load previously discovered symbols and their performance data
        historical_symbols = self.load_historical_symbols()
        performance_data = self.load_performance_data()
        
        # Update discovery weights based on historical performance
        self._update_discovery_weights(performance_data)
        
        # Method 1: Discover major market indices/components
        print("1. Discovering from major market indices...")
        index_symbols = self._discover_indices_autonomously()
        for symbol in index_symbols:
            self._tag_symbol_source(symbol, "indices", performance_data)
        all_symbols.update(index_symbols)
        print(f"   Found {len(index_symbols)} symbols from indices")
        
        # Method 2: Discover ETFs and their components
        print("2. Discovering from ETF universe...")
        etf_symbols = self._discover_etfs_autonomously()
        for symbol in etf_symbols:
            self._tag_symbol_source(symbol, "etfs", performance_data)
        all_symbols.update(etf_symbols)
        print(f"   Found {len(etf_symbols)} symbols from ETFs")
        
        # Method 3: Mine financial news for stock mentions
        print("3. Mining financial news for stock symbols...")
        news_symbols = self._mine_news_for_symbols()
        for symbol in news_symbols:
            self._tag_symbol_source(symbol, "news", performance_data)
        all_symbols.update(news_symbols)
        print(f"   Found {len(news_symbols)} symbols from news")
        
        # Method 4: Analyze market sectors
        print("4. Analyzing market sectors...")
        sector_symbols = self._analyze_sectors_autonomously()
        for symbol in sector_symbols:
            self._tag_symbol_source(symbol, "sectors", performance_data)
        all_symbols.update(sector_symbols)
        print(f"   Found {len(sector_symbols)} symbols from sectors")
        
        # Method 5: Discover from trending topics
        print("5. Discovering from trending topics...")
        trending_symbols = self._discover_trending_topics()
        for symbol in trending_symbols:
            self._tag_symbol_source(symbol, "trending", performance_data)
        all_symbols.update(trending_symbols)
        print(f"   Found {len(trending_symbols)} symbols from trending topics")
        
        # Method 6: Scrape from financial websites
        print("6. Scraping financial websites...")
        website_symbols = self._scrape_financial_websites()
        for symbol in website_symbols:
            self._tag_symbol_source(symbol, "websites", performance_data)
        all_symbols.update(website_symbols)
        print(f"   Found {len(website_symbols)} symbols from financial websites")
        
        # Method 7: Incorporate historical symbols with good performance
        print("7. Incorporating historical symbols with good performance...")
        historical_good_symbols = self._filter_good_historical_symbols(historical_symbols, performance_data)
        all_symbols.update(historical_good_symbols)
        print(f"   Added {len(historical_good_symbols)} high-performing historical symbols")
        
        print(f"\n=== DISCOVERY COMPLETE WITH LEARNING ===")
        print(f"Discovered {len(all_symbols)} unique stock symbols")
        
        # Save the discovered symbols for future runs
        self.save_historical_symbols(all_symbols)
        
        return all_symbols
    
    def _tag_symbol_source(self, symbol: str, source: str, performance_data: Dict):
        """Tag a symbol with its discovery source for learning purposes"""
        if symbol not in performance_data:
            performance_data[symbol] = {"sources": [], "performance": [], "last_price": None, "discovery_date": datetime.now().strftime('%Y-%m-%d')}
        
        if source not in performance_data[symbol]["sources"]:
            performance_data[symbol]["sources"].append(source)
            
    def _update_discovery_weights(self, performance_data: Dict):
        """Update discovery method weights based on historical performance"""
        if not performance_data:
            return
            
        # Calculate average performance for each discovery source
        source_performance = {
            'indices': [],
            'etfs': [],
            'news': [],
            'sectors': [],
            'trending': [],
            'websites': []
        }
        
        for symbol, data in performance_data.items():
            if "performance" in data and data["performance"]:
                avg_perf = sum(data["performance"]) / len(data["performance"])
                for source in data.get("sources", []):
                    if source in source_performance:
                        source_performance[source].append(avg_perf)
        
        # Calculate average performance for each source
        for source, performances in source_performance.items():
            if performances:
                avg = sum(performances) / len(performances)
                # Scale between 0.5 and 2.0
                self.discovery_weights[source] = max(0.5, min(2.0, 1.0 + avg))
                print(f"   Learning: {source} discovery weight adjusted to {self.discovery_weights[source]:.2f}")
            else:
                self.discovery_weights[source] = 1.0
    
    def _filter_good_historical_symbols(self, historical_symbols: Set[str], performance_data: Dict) -> Set[str]:
        """Filter historical symbols to keep only those with good performance"""
        good_symbols = set()
        
        for symbol in historical_symbols:
            if symbol in performance_data:
                data = performance_data[symbol]
                # Symbol has performance data and average performance is positive
                if "performance" in data and data["performance"] and sum(data["performance"]) > 0:
                    good_symbols.add(symbol)
        
        return good_symbols
    
    def load_historical_symbols(self) -> Set[str]:
        """Load historically discovered symbols from storage"""
        if not os.path.exists(self.historical_data_path):
            return set()
            
        try:
            with open(self.historical_data_path, 'r') as f:
                data = json.load(f)
                return set(data.get("symbols", []))
        except Exception as e:
            print(f"Error loading historical symbols: {e}")
            return set()
    
    def save_historical_symbols(self, symbols: Set[str]):
        """Save discovered symbols to storage for future runs"""
        try:
            data = {"symbols": list(symbols), "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            with open(self.historical_data_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving historical symbols: {e}")
    
    def load_performance_data(self) -> Dict:
        """Load performance data of previously discovered symbols"""
        if not os.path.exists(self.performance_history_path):
            return {}
            
        try:
            with open(self.performance_history_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading performance data: {e}")
            return {}
    
    def save_performance_data(self, performance_data: Dict):
        """Save performance data of symbols for learning"""
        try:
            with open(self.performance_history_path, 'w') as f:
                json.dump(performance_data, f)
        except Exception as e:
            print(f"Error saving performance data: {e}")
    
    def update_performance_data(self, symbols: Set[str], data_fetcher: DataFetcher):
        """Update performance data with latest prices and calculate returns"""
        print("\nUpdating performance data for learning...")
        performance_data = self.load_performance_data()
        updated_count = 0
        
        for symbol in symbols:
            try:
                # Get latest price
                fundamentals = data_fetcher.get_stock_fundamentals(symbol)
                if not fundamentals or 'price' not in fundamentals:
                    continue
                    
                current_price = fundamentals['price']
                
                # If symbol already in performance data
                if symbol in performance_data:
                    last_price = performance_data[symbol].get("last_price")
                    
                    # Calculate performance if we have a previous price
                    if last_price is not None and last_price > 0:
                        perf = (current_price - last_price) / last_price
                        performance_data[symbol]["performance"].append(perf)
                        # Keep only the most recent 5 performance measures
                        if len(performance_data[symbol]["performance"]) > 5:
                            performance_data[symbol]["performance"] = performance_data[symbol]["performance"][-5:]
                    
                    # Update last price
                    performance_data[symbol]["last_price"] = current_price
                    updated_count += 1
                else:
                    # Initialize new symbol data
                    performance_data[symbol] = {
                        "sources": [],
                        "performance": [],
                        "last_price": current_price,
                        "discovery_date": datetime.now().strftime('%Y-%m-%d')
                    }
                    updated_count += 1
                
                # Add some delay to prevent rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                continue
        
        print(f"Updated performance data for {updated_count} symbols")
        self.save_performance_data(performance_data)
        return performance_data
    
    def _discover_indices_autonomously(self) -> Set[str]:
        """Discover major indices completely from scratch"""
        symbols = set()
        
        try:
            # Adjust discovery based on learning weights
            indices_weight = self.discovery_weights.get('indices', 1.0)
            
            # Scrape Wikipedia for major indices and their components
            index_urls = [
                "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
                "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average",
                "https://en.wikipedia.org/wiki/NASDAQ-100",
                "https://en.wikipedia.org/wiki/Russell_1000_Index"
            ]
            
            # Add more URLs if this method has been historically successful
            if indices_weight > 1.5:
                index_urls.extend([
                    "https://en.wikipedia.org/wiki/Russell_2000_Index",
                    "https://en.wikipedia.org/wiki/S%26P_400"
                ])
            
            for url in index_urls:
                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Find all tables that might contain stock symbols
                        tables = soup.find_all('table', {'class': 'wikitable'})
                        
                        for table in tables:
                            # Look for ticker symbols (typically 1-5 uppercase letters)
                            rows = table.find_all('tr')
                            for row in rows:
                                cells = row.find_all('td')
                                if len(cells) > 1:
                                    # The symbol is usually in the first or second cell
                                    potential_symbol = cells[0].text.strip().upper()
                                    if self._is_potential_stock_symbol(potential_symbol):
                                        symbols.add(potential_symbol)
                                    
                                    if len(cells) > 1:
                                        potential_symbol = cells[1].text.strip().upper()
                                        if self._is_potential_stock_symbol(potential_symbol):
                                            symbols.add(potential_symbol)
                        
                        time.sleep(random.uniform(1, 3))
                except Exception as e:
                    print(f"Error scraping {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in index discovery: {e}")
            
        return symbols
    
    def _discover_etfs_autonomously(self) -> Set[str]:
        """Discover ETFs completely from scratch"""
        symbols = set()
        
        try:
            # Adjust discovery based on learning weights
            etfs_weight = self.discovery_weights.get('etfs', 1.0)
            
            # Scrape ETF databases
            etf_urls = [
                "https://etfdb.com/screener/#page=1",
                "https://www.zacks.com/funds/etf/",
                "https://www.etf.com/etfanalytics/etf-finder"
            ]
            
            # Add more URLs if this method has been historically successful
            if etfs_weight > 1.5:
                etf_urls.extend([
                    "https://www.invesco.com/us/financial-products/etfs",
                    "https://www.ishares.com/us/products/etf-investments"
                ])
            
            for base_url in etf_urls:
                try:
                    response = self.session.get(base_url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for ETF symbols (typically 3-5 uppercase letters)
                        text = soup.get_text()
                        potential_symbols = re.findall(r'\b[A-Z]{3,5}\b', text)
                        
                        for symbol in potential_symbols:
                            if self._is_potential_stock_symbol(symbol):
                                symbols.add(symbol)
                                
                        time.sleep(random.uniform(1, 3))
                except Exception as e:
                    print(f"Error scraping ETF URL: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in ETF discovery: {e}")
            
        return symbols
    
    def _mine_news_for_symbols(self) -> Set[str]:
        """Mine financial news completely from scratch for stock symbols"""
        symbols = set()
        
        try:
            # Adjust discovery based on learning weights
            news_weight = self.discovery_weights.get('news', 1.0)
            
            # Scrape financial news websites
            news_urls = [
                "https://www.bloomberg.com/markets",
                "https://www.reuters.com/business/finance/",
                "https://www.cnbc.com/markets/",
                "https://www.marketwatch.com/latest-news",
                "https://finance.yahoo.com/news/"
            ]
            
            # Add more URLs if this method has been historically successful
            if news_weight > 1.5:
                news_urls.extend([
                    "https://www.investors.com/news/",
                    "https://www.barrons.com/",
                    "https://www.fool.com/investing-news/"
                ])
            
            for url in news_urls:
                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract all text and look for stock symbols
                        text = soup.get_text()
                        potential_symbols = re.findall(r'\b[A-Z]{1,5}\b', text)
                        
                        for symbol in potential_symbols:
                            if self._is_potential_stock_symbol(symbol):
                                symbols.add(symbol)
                                
                        time.sleep(random.uniform(1, 3))
                except Exception as e:
                    print(f"Error scraping news URL {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in news mining: {e}")
            
        return symbols
    
    def _analyze_sectors_autonomously(self) -> Set[str]:
        """Analyze market sectors completely from scratch"""
        symbols = set()
        
        try:
            # Adjust discovery based on learning weights
            sectors_weight = self.discovery_weights.get('sectors', 1.0)
            
            # Scrape sector-specific pages
            sector_urls = [
                "https://www.sectorspdr.com/sectorspdr/",
                "https://www.fidelity.com/sector-investing/overview",
                "https://www.invesco.com/us/financial-products/etfs/sector-etfs"
            ]
            
            # Add more URLs if this method has been historically successful
            if sectors_weight > 1.5:
                sector_urls.extend([
                    "https://www.vaneck.com/us/en/investments/equity-etfs/",
                    "https://etfdb.com/etfs/sector/"
                ])
            
            for url in sector_urls:
                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for stock symbols in sector pages
                        text = soup.get_text()
                        potential_symbols = re.findall(r'\b[A-Z]{1,5}\b', text)
                        
                        for symbol in potential_symbols:
                            if self._is_potential_stock_symbol(symbol):
                                symbols.add(symbol)
                                
                        time.sleep(random.uniform(1, 3))
                except Exception as e:
                    print(f"Error scraping sector URL {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in sector analysis: {e}")
            
        return symbols
    
    def _discover_trending_topics(self) -> Set[str]:
        """Discover trending financial topics completely from scratch"""
        symbols = set()
        
        try:
            # Adjust discovery based on learning weights
            trending_weight = self.discovery_weights.get('trending', 1.0)
            
            # Scrape trending topics pages
            trending_urls = [
                "https://www.tradingview.com/markets/stocks-usa/market-movers-active/",
                "https://finviz.com/screener.ashx",
                "https://www.benzinga.com/movers"
            ]
            
            # Add more URLs if this method has been historically successful
            if trending_weight > 1.5:
                trending_urls.extend([
                    "https://www.barchart.com/stocks/market-movers/",
                    "https://stocktwits.com/trending"
                ])
            
            for url in trending_urls:
                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for stock symbols in trending pages
                        text = soup.get_text()
                        potential_symbols = re.findall(r'\b[A-Z]{1,5}\b', text)
                        
                        for symbol in potential_symbols:
                            if self._is_potential_stock_symbol(symbol):
                                symbols.add(symbol)
                                
                        time.sleep(random.uniform(1, 3))
                except Exception as e:
                    print(f"Error scraping trending URL {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in trending topics discovery: {e}")
            
        return symbols
    
    def _scrape_financial_websites(self) -> Set[str]:
        """Scrape additional financial websites for symbols"""
        symbols = set()
        
        try:
            # Adjust discovery based on learning weights
            websites_weight = self.discovery_weights.get('websites', 1.0)
            
            # Additional financial websites to scrape
            financial_urls = [
                "https://www.nasdaq.com/market-activity/stocks/screener",
                "https://www.nyse.com/listings_directory/stock",
                "https://www.investopedia.com/markets/"
            ]
            
            # Add more URLs if this method has been historically successful
            if websites_weight > 1.5:
                financial_urls.extend([
                    "https://www.wsj.com/market-data/stocks",
                    "https://www.morningstar.com/stocks"
                ])
            
            for url in financial_urls:
                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for stock symbols
                        text = soup.get_text()
                        potential_symbols = re.findall(r'\b[A-Z]{1,5}\b', text)
                        
                        for symbol in potential_symbols:
                            if self._is_potential_stock_symbol(symbol):
                                symbols.add(symbol)
                                
                        time.sleep(random.uniform(1, 3))
                except Exception as e:
                    print(f"Error scraping financial URL {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in financial website scraping: {e}")
            
        return symbols
    
    def _is_potential_stock_symbol(self, symbol: str) -> bool:
        """Determine if a string is potentially a stock symbol"""
        if not symbol or not isinstance(symbol, str):
            return False
            
        # Basic validation
        if not re.match(r'^[A-Z]{1,5}$', symbol):
            return False
            
        # Exclude obvious non-stock words
        non_stock_words = {
            'THE', 'AND', 'FOR', 'ARE', 'YOU', 'CAN', 'HAS', 'HAD', 'WAS', 'BEEN',
            'THAT', 'THIS', 'WITH', 'FROM', 'HAVE', 'WERE', 'WORD', 'WORK', 'WELL',
            'WANT', 'WILL', 'WHEN', 'WHAT', 'WEEK', 'MANY', 'MUCH', 'MORE', 'MOST',
            'NYSE', 'NASDAQ', 'ETF', 'SPDR', 'HTTP', 'HTML', 'COM', 'ORG', 'NET',
            'INC', 'CORP', 'LTD', 'CO', 'LLC', 'USA', 'USD', 'EUR', 'GBP', 'JPY'
        }
        
        if symbol in non_stock_words:
            return False
            
        return True
    
    def evaluate_opportunities(self, symbols: Set[str], data_fetcher: DataFetcher,
                             technical_analyzer: TechnicalAnalyzer,
                             catalyst_detector: CatalystDetector,
                             risk_manager: RiskManager) -> List[Dict]:
        """
        Evaluate all discovered symbols completely autonomously
        """
        print(f"\n=== AUTONOMOUS EVALUATION OF {len(symbols)} DISCOVERED SYMBOLS ===")
        
        # Update performance data for learning
        performance_data = self.update_performance_data(symbols, data_fetcher)
        
        # Apply learned insights to adjust evaluation criteria
        self._adjust_evaluation_criteria_from_learning(performance_data)
        
        # Reset progress tracker
        self.progress_tracker = ProgressTracker()
        
        # Record all symbols at G1 (Symbol Discovery)
        for symbol in symbols:
            self.progress_tracker.record_gate('G1', True)
        
        opportunities = []
        evaluated_count = 0
        
        for symbol in symbols:
            try:
                evaluated_count += 1
                
                # Render progress bars every 10 symbols
                if evaluated_count % 10 == 0:
                    self.progress_tracker.render_progress_bars()
                    print(f"Progress: {evaluated_count}/{len(symbols)} symbols evaluated")
                
                opportunity = self._evaluate_single_symbol(
                    symbol, data_fetcher, technical_analyzer,
                    catalyst_detector, risk_manager, performance_data
                )
                
                if opportunity and opportunity.get('overall_score', 0) > 0.2:
                    opportunities.append(opportunity)
                
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                continue  # Silent fail for autonomous operation
        
        # Final progress bar render
        self.progress_tracker.render_progress_bars()
        print(f"Completed evaluation. Found {len(opportunities)} qualifying opportunities.")
        return opportunities
    
    def _adjust_evaluation_criteria_from_learning(self, performance_data: Dict):
        """Adjust evaluation criteria based on historical performance data"""
        # Extract characteristics of top performing symbols
        top_performers = []
        
        for symbol, data in performance_data.items():
            if "performance" in data and len(data["performance"]) >= 2:
                avg_perf = sum(data["performance"]) / len(data["performance"])
                if avg_perf > 0.05:  # 5% average return threshold
                    top_performers.append((symbol, avg_perf, data))
        
        # Sort by performance
        top_performers.sort(key=lambda x: x[1], reverse=True)
        
        # Analyze top 10% or at least 5 symbols
        analysis_count = max(5, int(len(top_performers) * 0.1))
        top_performers = top_performers[:analysis_count]
        
        if top_performers:
            print(f"\nLearning from {analysis_count} top performing symbols...")
            
            # Initialize counters for analysis
            source_counts = {}
            for source in self.discovery_weights.keys():
                source_counts[source] = 0
                
            # Count how many top performers came from each source
            for _, _, data in top_performers:
                for source in data.get("sources", []):
                    if source in source_counts:
                        source_counts[source] += 1
            
            # Adjust weights again based on top performers
            total = sum(source_counts.values())
            if total > 0:
                for source, count in source_counts.items():
                    if count > 0:
                        # Boost sources that yield top performers
                        boost = (count / total) * 2
                        self.discovery_weights[source] = max(0.5, min(3.0, self.discovery_weights[source] + boost))
                        print(f"   Learning boost: {source} discovery weight further adjusted to {self.discovery_weights[source]:.2f}")
    
    def _evaluate_single_symbol(self, symbol: str, data_fetcher: DataFetcher,
                              technical_analyzer: TechnicalAnalyzer,
                              catalyst_detector: CatalystDetector,
                              risk_manager: RiskManager,
                              performance_data: Dict = None) -> Dict:
        """
        Evaluate a single symbol completely autonomously
        """
        try:
            # G2: Get fundamental data
            fundamentals = data_fetcher.get_stock_fundamentals(symbol)
            if not fundamentals:
                self.progress_tracker.record_gate('G2', False)
                return None
            self.progress_tracker.record_gate('G2', True)
            
            # G3: Price Validation
            current_price = fundamentals.get('price', 0)
            if current_price <= 0:
                self.progress_tracker.record_gate('G3', False)
                return None
            self.progress_tracker.record_gate('G3', True)
            
            # Determine if it's an opportunity
            is_opportunity = current_price <= 100.0  # Extended range
            is_penny_stock = (self.config.PENNY_STOCK_MIN_PRICE <= 
                            current_price <= self.config.PENNY_STOCK_MAX_PRICE)
            
            # G4: Get historical data
            historical_data = data_fetcher.get_historical_data(symbol, '3mo')
            if historical_data.empty:
                self.progress_tracker.record_gate('G4', False)
                return None
            self.progress_tracker.record_gate('G4', True)
            
            # G5: Technical analysis
            try:
                technical_data = technical_analyzer.calculate_all_indicators(historical_data)
                trend = technical_analyzer.identify_trend(technical_data)
                momentum_score = technical_analyzer.calculate_momentum_score(technical_data)
                technical_patterns = technical_analyzer.detect_technical_patterns(technical_data)
                self.progress_tracker.record_gate('G5', True)
            except Exception as e:
                self.progress_tracker.record_gate('G5', False)
                return None
            
            # G6: Catalyst analysis
            try:
                catalyst_score = catalyst_detector.calculate_catalyst_score(symbol, historical_data)
                news_sentiment = catalyst_detector.analyze_news_sentiment(symbol)
                self.progress_tracker.record_gate('G6', True)
            except Exception as e:
                self.progress_tracker.record_gate('G6', False)
                return None
            
            # G7: Volume analysis
            try:
                if len(historical_data) > 0:
                    current_volume = historical_data['Volume'].iloc[-1]
                    volume_analysis = catalyst_detector.detect_volume_anomalies(
                        symbol, current_volume, historical_data
                    )
                    volume_ratio = volume_analysis.get('volume_ratio', 1.0)
                else:
                    volume_ratio = 1.0
                self.progress_tracker.record_gate('G7', True)
            except Exception as e:
                self.progress_tracker.record_gate('G7', False)
                return None
            
            # Apply learning insights
            learning_boost = 0.0
            if performance_data and symbol in performance_data:
                # If symbol has had good performance in the past, boost its score
                symbol_data = performance_data[symbol]
                if "performance" in symbol_data and symbol_data["performance"]:
                    avg_perf = sum(symbol_data["performance"]) / len(symbol_data["performance"])
                    if avg_perf > 0:  # Positive average return
                        learning_boost = min(avg_perf * 2, 0.3)  # Cap at 30% boost
            
            # G8: Calculate scores
            try:
                confidence_score = self._calculate_confidence_score(
                    momentum_score, catalyst_score, volume_ratio, 
                    news_sentiment, trend, technical_patterns
                )
                
                overall_score = self._calculate_overall_score(
                    momentum_score, catalyst_score, confidence_score,
                    is_penny_stock, technical_patterns, learning_boost
                )
                self.progress_tracker.record_gate('G8', True)
            except Exception as e:
                self.progress_tracker.record_gate('G8', False)
                return None
            
            # G9: Risk Assessment (Risk management calculations)
            try:
                stop_loss = risk_manager.calculate_stop_loss(current_price)
                take_profit = risk_manager.calculate_take_profit(current_price, stop_loss)
                risk_reward_ratio = risk_manager.calculate_risk_reward_ratio(
                    current_price, stop_loss, take_profit
                )
                
                # Validate risk parameters
                if stop_loss <= 0 or take_profit <= 0 or risk_reward_ratio < 1.0:
                    self.progress_tracker.record_gate('G9', False)
                    return None
                
                self.progress_tracker.record_gate('G9', True)
            except Exception as e:
                self.progress_tracker.record_gate('G9', False)
                return None
            
            # G10: Final Position (Final validation based on overall score)
            if overall_score <= 0.2:
                self.progress_tracker.record_gate('G10', False)
                return None
            
            self.progress_tracker.record_gate('G10', True)
            
            return {
                'symbol': symbol,
                'company_name': fundamentals.get('company_name', symbol),
                'sector': fundamentals.get('sector', 'Unknown'),
                'price': current_price,
                'market_cap': fundamentals.get('market_cap', 0),
                'trend': trend,
                'momentum_score': momentum_score,
                'catalyst_score': catalyst_score,
                'sentiment_score': news_sentiment.get('sentiment_score', 0),
                'buzz_score': news_sentiment.get('buzz_score', 0),
                'volume_ratio': volume_ratio,
                'confidence_score': confidence_score,
                'overall_score': overall_score,
                'learning_boost': learning_boost,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'risk_reward_ratio': risk_reward_ratio,
                'is_penny_stock': is_penny_stock,
                'patterns_count': len(technical_patterns),
                'pe_ratio': fundamentals.get('pe_ratio', np.nan),
                'beta': fundamentals.get('beta', 1.0)
            }
            
        except Exception as e:
            return None
    
    def _calculate_confidence_score(self, momentum_score: float, catalyst_score: float,
                                  volume_ratio: float, sentiment: Dict, trend: str,
                                  technical_patterns: Dict) -> float:
        """
        Calculate confidence score for the opportunity
        """
        score = 0.0
        
        # Momentum contribution (0-25 points)
        score += (momentum_score + 1) * 12.5  # Convert from -1,1 to 0,25 scale
        
        # Catalyst contribution (0-20 points)
        score += catalyst_score * 20
        
        # Volume contribution (0-15 points)
        if volume_ratio >= 3:
            score += 15
        elif volume_ratio >= 2:
            score += 10
        elif volume_ratio >= 1.5:
            score += 5
        
        # Sentiment contribution (0-15 points)
        composite_sentiment = sentiment.get('composite_score', 0)
        score += composite_sentiment * 15
        
        # Trend contribution (0-15 points)
        trend_scores = {
            'Strong Bullish': 15,
            'Bullish': 10,
            'Neutral': 5,
            'Bearish': 0
        }
        score += trend_scores.get(trend, 5)
        
        # Technical patterns contribution (0-10 points)
        score += min(len(technical_patterns) * 3, 10)
        
        # Normalize to 0-1 range
        return min(score / 100.0, 1.0)
    
    def _calculate_overall_score(self, momentum_score: float, catalyst_score: float,
                               confidence_score: float, is_penny_stock: bool,
                               technical_patterns: Dict, learning_boost: float = 0.0) -> float:
        """
        Calculate overall score combining all factors
        """
        # Weighted combination of factors
        score = (
            (momentum_score + 1) * 20 +  # 20% momentum (normalized)
            catalyst_score * 20 +  # 20% catalysts
            confidence_score * 20 +  # 20% confidence
            min(len(technical_patterns), 5) * 3 +  # 15% technical patterns
            (10 if is_penny_stock else 0) +  # 10% penny stock bonus
            learning_boost * 100  # Add learning boost (up to 15%)
        )
        
        # Normalize to 0-1 range
        return min(score / 100.0, 1.0)

# Example usage
if __name__ == "__main__":
    pass
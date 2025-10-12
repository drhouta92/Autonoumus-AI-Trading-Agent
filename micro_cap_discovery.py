"""
Micro-Cap Discovery Module
Specialized discovery engine for micro-cap and penny stocks with advanced filtering
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Set, Optional
import time
import random

class MicroCapDiscovery:
    """
    Specialized discovery for micro-cap stocks (< $300M market cap)
    Includes penny stock detection and filtering
    """
    
    def __init__(self, config, brain_manager=None):
        self.config = config
        self.brain_manager = brain_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Micro-cap specific parameters
        self.max_market_cap = 300_000_000  # $300M
        self.min_market_cap = 5_000_000    # $5M (avoid nano-caps)
        self.penny_stock_max_price = 5.0    # NYSE/NASDAQ definition
        self.penny_stock_min_price = 0.10
        self.min_daily_volume = 50_000
        self.min_avg_volume = 100_000
        
    def discover_micro_caps(self) -> Set[str]:
        """
        Discover micro-cap stocks from multiple specialized sources
        """
        print("=== MICRO-CAP DISCOVERY ENGINE ===")
        all_symbols = set()
        
        # Method 1: Scan small-cap ETF holdings
        print("1. Scanning small-cap ETF holdings...")
        etf_symbols = self._scan_smallcap_etfs()
        all_symbols.update(etf_symbols)
        print(f"   Found {len(etf_symbols)} symbols from ETFs")
        
        # Method 2: Scrape penny stock screeners
        print("2. Scraping penny stock screeners...")
        penny_symbols = self._scrape_penny_screeners()
        all_symbols.update(penny_symbols)
        print(f"   Found {len(penny_symbols)} symbols from screeners")
        
        # Method 3: Mine micro-cap news sources
        print("3. Mining micro-cap news sources...")
        news_symbols = self._mine_microcap_news()
        all_symbols.update(news_symbols)
        print(f"   Found {len(news_symbols)} symbols from news")
        
        # Method 4: Scan OTC markets
        print("4. Scanning OTC/Pink Sheet markets...")
        otc_symbols = self._scan_otc_markets()
        all_symbols.update(otc_symbols)
        print(f"   Found {len(otc_symbols)} symbols from OTC")
        
        # Method 5: Discover from volume spikes
        print("5. Detecting unusual volume spikes...")
        volume_symbols = self._detect_volume_spikes()
        all_symbols.update(volume_symbols)
        print(f"   Found {len(volume_symbols)} symbols with volume spikes")
        
        print(f"\n✅ Total discovered: {len(all_symbols)} micro-cap symbols")
        return all_symbols
    
    def _scan_smallcap_etfs(self) -> Set[str]:
        """Scan holdings of small-cap focused ETFs"""
        symbols = set()
        
        # Small-cap ETFs
        smallcap_etfs = ['IWM', 'VTWO', 'SCHA', 'IJR', 'VBR', 'SLYG', 'SLYV']
        
        for etf in smallcap_etfs:
            try:
                ticker = yf.Ticker(etf)
                # Try to get holdings (not always available)
                # Alternative: get related stocks
                info = ticker.info
                if info:
                    symbols.add(etf)
                time.sleep(0.5)
            except Exception as e:
                pass
        
        # Add known small-cap symbols from sector analysis
        additional = self._get_sector_smallcaps()
        symbols.update(additional)
        
        return symbols
    
    def _get_sector_smallcaps(self) -> Set[str]:
        """Get small-cap symbols by sector scanning"""
        symbols = set()
        
        # Sectors with micro-cap opportunities
        sectors = ['Biotechnology', 'Technology', 'Healthcare', 'Energy', 'Materials']
        
        # This is a simplified approach - in production would use proper screener API
        # For now, we'll use a representative set
        known_microcaps = [
            'ENZC', 'HALB', 'RETC', 'MINE', 'HEMP',  # OTC examples
            'EXPR', 'CARV', 'TOPS', 'SHIP', 'GNUS'   # Listed examples
        ]
        
        symbols.update(known_microcaps)
        return symbols
    
    def _scrape_penny_screeners(self) -> Set[str]:
        """Scrape popular penny stock screeners"""
        symbols = set()
        
        # Finviz penny stock screener
        try:
            url = "https://finviz.com/screener.ashx?v=111&f=cap_microunder,sh_price_u5&ft=4"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Extract ticker symbols
                ticker_links = soup.find_all('a', {'class': 'tab-link'})
                for link in ticker_links:
                    symbol = link.text.strip()
                    if symbol and len(symbol) <= 5:
                        symbols.add(symbol)
            time.sleep(1)
        except Exception as e:
            print(f"   Error scraping Finviz: {e}")
        
        # Add from pattern
        additional_patterns = self._extract_from_market_patterns()
        symbols.update(additional_patterns)
        
        return symbols
    
    def _extract_from_market_patterns(self) -> Set[str]:
        """Extract symbols matching micro-cap patterns"""
        symbols = set()
        
        # Common micro-cap ticker patterns
        # 4-letter tickers ending in specific patterns
        base_tickers = ['ABCD', 'WXYZ', 'TECH', 'BIOX', 'GENO']
        
        # This would need real market data - placeholder for structure
        return symbols
    
    def _mine_microcap_news(self) -> Set[str]:
        """Mine micro-cap focused news sources"""
        symbols = set()
        
        news_sources = [
            "https://www.otcmarkets.com/research/stock-screener",
            "https://www.pennystockflow.com",
            "https://microcapdaily.com"
        ]
        
        for source in news_sources:
            try:
                response = self.session.get(source, timeout=10)
                if response.status_code == 200:
                    # Extract ticker symbols (pattern: $SYMBOL or SYMBOL:)
                    text = response.text
                    ticker_pattern = r'\$([A-Z]{1,5})\b'
                    found = re.findall(ticker_pattern, text)
                    symbols.update(found)
                time.sleep(1)
            except Exception as e:
                pass
        
        return symbols
    
    def _scan_otc_markets(self) -> Set[str]:
        """Scan OTC and Pink Sheet markets"""
        symbols = set()
        
        # OTC Market tiers
        try:
            # OTCQB and OTCQX are higher quality
            url = "https://www.otcmarkets.com/market-activity/current-market"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Extract symbols from table
                rows = soup.find_all('tr')
                for row in rows[:50]:  # Limit to top 50
                    cells = row.find_all('td')
                    if cells:
                        symbol_cell = cells[0].text.strip()
                        if len(symbol_cell) <= 5:
                            symbols.add(symbol_cell)
        except Exception as e:
            pass
        
        return symbols
    
    def _detect_volume_spikes(self) -> Set[str]:
        """Detect stocks with unusual volume activity"""
        symbols = set()
        
        # This would connect to real-time data feed
        # For now, use a heuristic approach
        
        # Check recent movers with volume
        try:
            # Using yfinance to check some known volatile micro-caps
            test_symbols = ['SIRI', 'NAK', 'PLUG', 'SOLO', 'WKHS']
            
            for symbol in test_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='5d')
                    if not hist.empty and len(hist) >= 2:
                        # Check for volume spike
                        recent_vol = hist['Volume'].iloc[-1]
                        avg_vol = hist['Volume'].mean()
                        if recent_vol > avg_vol * 2.0:
                            symbols.add(symbol)
                    time.sleep(0.5)
                except Exception:
                    pass
        except Exception as e:
            pass
        
        return symbols
    
    def filter_micro_caps(self, symbols: Set[str]) -> List[Dict]:
        """
        Filter discovered symbols for true micro-cap criteria
        Returns list of qualified symbols with metadata
        """
        print(f"\n🔍 Filtering {len(symbols)} symbols for micro-cap criteria...")
        qualified = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if not info:
                    continue
                
                # Get key metrics
                market_cap = info.get('marketCap', 0)
                price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                volume = info.get('volume', 0)
                avg_volume = info.get('averageVolume', 0)
                
                # Apply filters
                if not self._passes_filters(market_cap, price, volume, avg_volume):
                    continue
                
                # Classify
                is_penny = self._is_penny_stock(price)
                is_micro = self._is_micro_cap(market_cap)
                
                qualified.append({
                    'symbol': symbol,
                    'market_cap': market_cap,
                    'price': price,
                    'volume': volume,
                    'avg_volume': avg_volume,
                    'is_penny_stock': is_penny,
                    'is_micro_cap': is_micro,
                    'sector': info.get('sector', 'Unknown'),
                    'exchange': info.get('exchange', 'Unknown')
                })
                
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                continue
        
        print(f"✅ Qualified: {len(qualified)} micro-cap stocks")
        return qualified
    
    def _passes_filters(self, market_cap: float, price: float, 
                       volume: int, avg_volume: int) -> bool:
        """Check if stock passes micro-cap filters"""
        
        # Market cap filter
        if market_cap <= 0 or market_cap > self.max_market_cap:
            return False
        
        if market_cap < self.min_market_cap:
            return False
        
        # Price filter
        if price <= 0 or price < self.penny_stock_min_price:
            return False
        
        # Volume filter (ensure liquidity)
        if volume < self.min_daily_volume:
            return False
        
        if avg_volume < self.min_avg_volume:
            return False
        
        return True
    
    def _is_penny_stock(self, price: float) -> bool:
        """Determine if stock qualifies as penny stock"""
        return self.penny_stock_min_price <= price <= self.penny_stock_max_price
    
    def _is_micro_cap(self, market_cap: float) -> bool:
        """Determine if stock qualifies as micro-cap"""
        return self.min_market_cap <= market_cap <= self.max_market_cap
    
    def rank_by_opportunity(self, filtered_stocks: List[Dict]) -> List[Dict]:
        """
        Rank micro-caps by opportunity score
        """
        print("\n📊 Ranking micro-caps by opportunity score...")
        
        for stock in filtered_stocks:
            score = 0.0
            
            # Volume score (higher is better for liquidity)
            if stock['avg_volume'] > 500_000:
                score += 0.3
            elif stock['avg_volume'] > 200_000:
                score += 0.2
            else:
                score += 0.1
            
            # Market cap sweet spot (not too small, not too large)
            if 50_000_000 <= stock['market_cap'] <= 150_000_000:
                score += 0.3
            elif 20_000_000 <= stock['market_cap'] <= 200_000_000:
                score += 0.2
            
            # Price action (penny stocks get bonus for volatility potential)
            if stock['is_penny_stock']:
                score += 0.2
            
            # Volume surge indicator
            if stock['volume'] > stock['avg_volume'] * 1.5:
                score += 0.2
            
            stock['opportunity_score'] = score
        
        # Sort by opportunity score
        ranked = sorted(filtered_stocks, key=lambda x: x['opportunity_score'], reverse=True)
        
        print(f"✅ Top opportunity score: {ranked[0]['opportunity_score']:.2f}" if ranked else "No stocks ranked")
        return ranked
    
    def get_discovery_stats(self) -> Dict:
        """Get statistics about discovery process"""
        return {
            'max_market_cap': self.max_market_cap,
            'min_market_cap': self.min_market_cap,
            'penny_stock_range': f"${self.penny_stock_min_price:.2f} - ${self.penny_stock_max_price:.2f}",
            'min_daily_volume': self.min_daily_volume,
            'min_avg_volume': self.min_avg_volume
        }

# Example usage
if __name__ == "__main__":
    import config
    discovery = MicroCapDiscovery(config)
    symbols = discovery.discover_micro_caps()
    filtered = discovery.filter_micro_caps(symbols)
    ranked = discovery.rank_by_opportunity(filtered)
    print(f"\nTop 5 opportunities:")
    for i, stock in enumerate(ranked[:5], 1):
        print(f"{i}. {stock['symbol']} - Score: {stock['opportunity_score']:.2f}")

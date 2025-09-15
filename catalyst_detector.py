import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re
import requests
from bs4 import BeautifulSoup
import time
import random

class CatalystDetector:
    def __init__(self, config, data_fetcher):
        self.config = config
        self.data_fetcher = data_fetcher
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def analyze_news_sentiment(self, symbol: str) -> Dict:
        """
        Analyze news sentiment for a symbol using web scraping in addition to Finnhub
        """
        # First try Finnhub API
        sentiment_data = self.data_fetcher.get_news_sentiment(symbol)
        
        # Then enhance with web scraping
        scraped_sentiment = self._scrape_news_sentiment(symbol)
        
        # Combine results
        sentiment_score = sentiment_data.get('sentiment', {}).get('score', 0.0) or scraped_sentiment.get('sentiment_score', 0.0)
        buzz_score = sentiment_data.get('buzz', {}).get('score', 0.0) or scraped_sentiment.get('buzz_score', 0.0)
        articles_count = sentiment_data.get('buzz', {}).get('articlesInLastWeek', 0) or scraped_sentiment.get('articles_count', 0)
        
        # Calculate composite score
        composite_score = (float(sentiment_score) * 0.7 + float(buzz_score) * 0.3) if sentiment_score is not None and buzz_score is not None else 0.0
        
        return {
            'sentiment_score': float(sentiment_score) if sentiment_score is not None else 0.0,
            'buzz_score': float(buzz_score) if buzz_score is not None else 0.0,
            'articles_count': int(articles_count) if articles_count is not None else 0,
            'composite_score': composite_score
        }
    
    def _scrape_news_sentiment(self, symbol: str) -> Dict:
        """
        Scrape news sentiment from financial websites
        """
        sentiment_score = 0.0
        buzz_score = 0.0
        articles_count = 0
        
        try:
            # Scrape news from multiple sources
            news_sources = [
                f"https://finviz.com/quote.ashx?t={symbol}",
                f"https://www.benzinga.com/quote/{symbol}",
                f"https://www.tradingview.com/symbols/{symbol}/news/",
                f"https://www.marketwatch.com/investing/stock/{symbol}/news"
            ]
            
            positive_keywords = ['up', 'rise', 'gain', 'surge', 'jump', 'beat', 'positive', 'bullish', 'strong', 'growth']
            negative_keywords = ['down', 'fall', 'drop', 'plunge', 'miss', 'negative', 'bearish', 'weak', 'decline', 'loss']
            
            all_headlines = []
            
            for url in news_sources:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract headlines
                        headlines = []
                        for headline in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a']):
                            text = headline.get_text().strip()
                            if text and len(text) > 10 and symbol.lower() in text.lower():
                                headlines.append(text)
                        
                        all_headlines.extend(headlines)
                        
                        # Count articles
                        articles_count += len(headlines)
                        
                        time.sleep(random.uniform(1, 2))
                except:
                    continue
            
            # Analyze sentiment from headlines
            if all_headlines:
                positive_count = 0
                negative_count = 0
                
                for headline in all_headlines:
                    headline_lower = headline.lower()
                    
                    # Check for positive keywords
                    if any(keyword in headline_lower for keyword in positive_keywords):
                        positive_count += 1
                    
                    # Check for negative keywords
                    if any(keyword in headline_lower for keyword in negative_keywords):
                        negative_count += 1
                
                # Calculate sentiment score (-1 to 1)
                if positive_count + negative_count > 0:
                    sentiment_score = (positive_count - negative_count) / (positive_count + negative_count)
                
                # Calculate buzz score (0 to 1)
                buzz_score = min(len(all_headlines) / 20, 1.0)
        
        except Exception as e:
            print(f"Error scraping news sentiment for {symbol}: {e}")
        
        return {
            'sentiment_score': sentiment_score,
            'buzz_score': buzz_score,
            'articles_count': articles_count
        }
    
    def detect_volume_anomalies(self, symbol: str, current_volume: float, 
                              historical_data: pd.DataFrame) -> Dict:
        """
        Detect unusual volume activity
        """
        try:
            if historical_data.empty or len(historical_data) < 20:
                return {'is_anomaly': False, 'volume_ratio': 1.0}
            
            avg_volume = historical_data['Volume'].tail(20).mean()
            
            if avg_volume > 0 and current_volume is not None:
                volume_ratio = current_volume / avg_volume
                is_anomaly = volume_ratio >= self.config.VOLUME_SPIKE_THRESHOLD
            else:
                volume_ratio = 1.0
                is_anomaly = False
            
            return {
                'is_anomaly': is_anomaly,
                'volume_ratio': volume_ratio,
                'avg_volume': avg_volume,
                'current_volume': current_volume
            }
        except Exception as e:
            print(f"Error detecting volume anomalies for {symbol}: {e}")
            return {'is_anomaly': False, 'volume_ratio': 1.0}
    
    def scrape_catalysts_from_news(self, symbol: str) -> Dict:
        """
        Scrape catalyst information from company news using web scraping
        """
        catalysts = {
            'fda_mentions': 0,
            'patent_mentions': 0,
            'ma_mentions': 0,
            'contract_mentions': 0,
            'earnings_mentions': 0,
            'total_catalyst_score': 0.0
        }
        
        try:
            # Get news from API first
            api_news = self.data_fetcher.get_company_news(symbol, days=30)
            
            # Then scrape additional news from websites
            scraped_news = self._scrape_company_news(symbol)
            
            # Combine all news
            all_news = api_news + scraped_news
            
            if not all_news:
                return catalysts
            
            # Keywords for different catalyst types
            fda_keywords = ['fda approval', 'regulatory approval', 'fda clearance', 'drug approval', 'clinical trial']
            patent_keywords = ['patent', 'intellectual property', 'ip rights', 'patent granted', 'patent application']
            ma_keywords = ['acquisition', 'merger', 'takeover', 'buyout', 'acquired', 'bid', 'offer', 'purchase']
            contract_keywords = ['contract', 'partnership', 'joint venture', 'deal worth', 'funding', 'investment', 'government contract']
            earnings_keywords = ['earnings', 'quarterly results', 'profit', 'revenue', 'beat', 'miss']
            
            for article in all_news[:30]:  # Analyze up to 30 articles
                title = article.get('headline', '').lower() if isinstance(article, dict) else str(article).lower()
                summary = article.get('summary', '').lower() if isinstance(article, dict) else ''
                full_text = title + ' ' + summary
                
                # Count mentions for each catalyst type
                if any(keyword in full_text for keyword in fda_keywords):
                    catalysts['fda_mentions'] += 1
                if any(keyword in full_text for keyword in patent_keywords):
                    catalysts['patent_mentions'] += 1
                if any(keyword in full_text for keyword in ma_keywords):
                    catalysts['ma_mentions'] += 1
                if any(keyword in full_text for keyword in contract_keywords):
                    catalysts['contract_mentions'] += 1
                if any(keyword in full_text for keyword in earnings_keywords):
                    catalysts['earnings_mentions'] += 1
            
            # Calculate weighted catalyst score
            weights = {
                'fda': 0.25,
                'patent': 0.15,
                'ma': 0.25,
                'contract': 0.20,
                'earnings': 0.15
            }
            
            total_score = (
                min(catalysts['fda_mentions'] * 0.2, 1.0) * weights['fda'] +
                min(catalysts['patent_mentions'] * 0.15, 1.0) * weights['patent'] +
                min(catalysts['ma_mentions'] * 0.3, 1.0) * weights['ma'] +
                min(catalysts['contract_mentions'] * 0.2, 1.0) * weights['contract'] +
                min(catalysts['earnings_mentions'] * 0.15, 1.0) * weights['earnings']
            )
            
            catalysts['total_catalyst_score'] = min(total_score, 1.0)
            
        except Exception as e:
            print(f"Error scraping catalysts for {symbol}: {e}")
        
        return catalysts
    
    def _scrape_company_news(self, symbol: str) -> List[Dict]:
        """
        Scrape company news from financial websites
        """
        news_items = []
        
        try:
            # Scrape news from multiple sources
            news_sources = [
                f"https://finviz.com/quote.ashx?t={symbol}",
                f"https://www.benzinga.com/quote/{symbol}",
                f"https://www.tradingview.com/symbols/{symbol}/news/",
                f"https://www.marketwatch.com/investing/stock/{symbol}/news"
            ]
            
            for url in news_sources:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract news items (implementation varies by site)
                        # This is a simplified example
                        news_elements = soup.find_all(['article', 'div'], class_=re.compile(r'news|article|headline', re.I))
                        
                        for element in news_elements[:5]:  # Get up to 5 news items per source
                            headline = element.get_text().strip()
                            if headline and len(headline) > 10:
                                news_items.append({
                                    'headline': headline,
                                    'summary': '',
                                    'source': url
                                })
                        
                        time.sleep(random.uniform(1, 2))
                except:
                    continue
                    
        except Exception as e:
            print(f"Error scraping company news for {symbol}: {e}")
        
        return news_items
    
    def calculate_catalyst_score(self, symbol: str, historical_data: pd.DataFrame) -> float:
        """
        Calculate overall catalyst score for a symbol
        """
        try:
            # Get news sentiment
            sentiment = self.analyze_news_sentiment(symbol)
            sentiment_score = sentiment.get('composite_score', 0)
            
            # Get current volume for anomaly detection
            if not historical_data.empty:
                current_volume = historical_data['Volume'].iloc[-1]
                volume_analysis = self.detect_volume_anomalies(symbol, current_volume, historical_data)
                volume_ratio = volume_analysis.get('volume_ratio', 1.0)
            else:
                volume_ratio = 1.0
            
            # Scrape catalysts from news
            news_catalysts = self.scrape_catalysts_from_news(symbol)
            news_catalyst_score = news_catalysts.get('total_catalyst_score', 0)
            
            # Calculate weighted score
            score = (
                sentiment_score * 0.4 +  # 40% sentiment
                min(volume_ratio / 5, 1.0) * 0.3 +  # 30% volume anomaly
                news_catalyst_score * 0.3  # 30% news catalysts
            )
            
            return min(score, 1.0)
        except Exception as e:
            print(f"Error calculating catalyst score for {symbol}: {e}")
            return 0.0

# Example usage
if __name__ == "__main__":
    pass
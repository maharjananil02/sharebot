"""
Market Analyzer - Fetches and analyzes NEPSE floor sheet data
Identifies trending stocks based on transaction volume and bulk purchases
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging
import re

from .logger import setup_logger

logger = setup_logger(__name__)


class MarketAnalyzer:
    """Analyzes NEPSE market data to identify trending stocks"""
    
    def __init__(self):
        self.logger = logger
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.stock_data = {}
        self.analysis_results = {}
    
    def fetch_all_stocks_data(self, source: str = "sharesansar") -> Dict:
        """
        Fetch data for all stocks from live trading page
        
        Args:
            source: "sharesansar" or "nepalstock"
            
        Returns:
            Dictionary with stock data: {symbol: {price, volume, transactions, change, etc}}
        """
        try:
            if source == "sharesansar":
                return self._fetch_from_sharesansar()
            elif source == "nepalstock":
                return self._fetch_from_nepalstock()
            else:
                raise ValueError(f"Unknown data source: {source}")
        except Exception as e:
            self.logger.error(f"Failed to fetch market data: {str(e)}")
            return {}
    
    def _fetch_from_sharesansar(self) -> Dict:
        """Fetch all stocks data from ShareSansar live trading page"""
        try:
            url = "https://www.sharesansar.com/live-trading"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            tables = soup.find_all('table')
            
            stocks = {}
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all('td')
                    
                    if len(cells) >= 9:
                        try:
                            # Column structure: S.No | Symbol | LTP | Point Change | % Change | Open | High | Low | Volume | Prev. Close
                            # Extract cells safely
                            sno_text = cells[0].get_text(strip=True)
                            symbol_text = cells[1].get_text(strip=True)
                            ltp_text = cells[2].get_text(strip=True)
                            change_text = cells[3].get_text(strip=True)
                            pct_change_text = cells[4].get_text(strip=True)
                            open_text = cells[5].get_text(strip=True)
                            high_text = cells[6].get_text(strip=True)
                            low_text = cells[7].get_text(strip=True)
                            volume_text = cells[8].get_text(strip=True)
                            
                            # Skip if any essential field is empty
                            if not all([symbol_text, ltp_text, volume_text]):
                                continue
                            
                            # Clean and extract symbol (remove any non-alphabetic characters)
                            symbol = ''.join(c for c in symbol_text if c.isalpha()).upper()
                            
                            if not symbol:
                                continue
                            
                            # Parse numeric values
                            ltp = float(ltp_text.replace(',', '').strip())
                            change = float(change_text.replace(',', '').strip())
                            pct_change_str = pct_change_text.replace('%', '').replace(',', '').strip()
                            pct_change = float(pct_change_str) if pct_change_str else 0.0
                            
                            open_price = float(open_text.replace(',', '').strip()) if open_text else ltp
                            high = float(high_text.replace(',', '').strip()) if high_text else ltp
                            low = float(low_text.replace(',', '').strip()) if low_text else ltp
                            
                            # Extract volume (remove commas and get first number)
                            volume_str = volume_text.replace(',', '').strip().split()[0]
                            volume = int(float(volume_str))
                            
                            # Validate price range
                            if ltp > 0 and 1 < ltp < 1000000:
                                stocks[symbol] = {
                                    'symbol': symbol,
                                    'ltp': ltp,
                                    'change': change,
                                    'pct_change': pct_change,
                                    'open': open_price,
                                    'high': high,
                                    'low': low,
                                    'volume': volume,
                                    'source': 'sharesansar',
                                    'fetch_time': datetime.now()
                                }
                        except (ValueError, IndexError, AttributeError) as e:
                            continue
            
            self.logger.info(f"✓ Fetched data for {len(stocks)} stocks from ShareSansar")
            self.stock_data = stocks
            return stocks
            
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Cannot connect to ShareSansar: {str(e)}")
            return {}
        except Exception as e:
            self.logger.error(f"Error fetching from ShareSansar: {str(e)}")
            return {}
    
    def _fetch_from_nepalstock(self) -> Dict:
        """Fetch all stocks data from Nepal Stock Exchange"""
        try:
            url = "https://www.nepalstock.com/today-price"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            tables = soup.find_all('table')
            
            stocks = {}
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all('td')
                    
                    if len(cells) >= 5:
                        try:
                            symbol = cells[0].get_text(strip=True).upper()
                            ltp = float(cells[1].get_text(strip=True).replace(',', ''))
                            change = float(cells[2].get_text(strip=True).replace(',', ''))
                            volume = int(cells[4].get_text(strip=True).replace(',', '').split()[0])
                            
                            if len(symbol) > 0 and ltp > 0:
                                pct_change = (change / (ltp - change) * 100) if (ltp - change) != 0 else 0
                                stocks[symbol] = {
                                    'symbol': symbol,
                                    'ltp': ltp,
                                    'change': change,
                                    'pct_change': pct_change,
                                    'volume': volume,
                                    'source': 'nepalstock',
                                    'fetch_time': datetime.now()
                                }
                        except (ValueError, IndexError, AttributeError):
                            continue
            
            self.logger.info(f"✓ Fetched data for {len(stocks)} stocks from Nepal Stock Exchange")
            self.stock_data = stocks
            return stocks
            
        except Exception as e:
            self.logger.error(f"Error fetching from Nepal Stock Exchange: {str(e)}")
            return {}
    
    def get_top_stocks_by_volume(self, top_n: int = 3, min_volume: int = 10000) -> List[Tuple[str, Dict]]:
        """
        Get top N stocks by trading volume
        
        Args:
            top_n: Number of top stocks to return (default 3)
            min_volume: Minimum volume threshold (default 10,000 shares)
            
        Returns:
            List of tuples: [(symbol, stock_data), ...]
        """
        if not self.stock_data:
            self.logger.warning("No stock data available. Call fetch_all_stocks_data() first.")
            return []
        
        # Filter by minimum volume
        filtered = {
            symbol: data 
            for symbol, data in self.stock_data.items() 
            if data.get('volume', 0) >= min_volume
        }
        
        # Sort by volume descending
        sorted_stocks = sorted(
            filtered.items(),
            key=lambda x: x[1].get('volume', 0),
            reverse=True
        )
        
        top_stocks = sorted_stocks[:top_n]
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"TOP {top_n} STOCKS BY VOLUME (Today)")
        self.logger.info(f"{'='*80}")
        
        for i, (symbol, data) in enumerate(top_stocks, 1):
            self.logger.info(
                f"{i}. {symbol}: {data['volume']:,} shares | "
                f"Price: Rs. {data['ltp']:.2f} | Change: {data['pct_change']:+.2f}%"
            )
        
        self.logger.info(f"{'='*80}\n")
        
        return top_stocks
    
    def get_top_stocks_by_price_change(self, top_n: int = 3, min_volume: int = 5000) -> List[Tuple[str, Dict]]:
        """
        Get top N stocks by positive price change (gainers)
        
        Args:
            top_n: Number of top stocks to return
            min_volume: Minimum volume threshold
            
        Returns:
            List of tuples: [(symbol, stock_data), ...]
        """
        if not self.stock_data:
            self.logger.warning("No stock data available.")
            return []
        
        # Filter by minimum volume and positive change
        filtered = {
            symbol: data 
            for symbol, data in self.stock_data.items() 
            if data.get('volume', 0) >= min_volume and data.get('pct_change', 0) > 0
        }
        
        # Sort by percentage change descending
        sorted_stocks = sorted(
            filtered.items(),
            key=lambda x: x[1].get('pct_change', 0),
            reverse=True
        )
        
        top_stocks = sorted_stocks[:top_n]
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"TOP {top_n} GAINERS (Today)")
        self.logger.info(f"{'='*80}")
        
        for i, (symbol, data) in enumerate(top_stocks, 1):
            self.logger.info(
                f"{i}. {symbol}: {data['pct_change']:+.2f}% | "
                f"Price: Rs. {data['ltp']:.2f} | Volume: {data['volume']:,}"
            )
        
        self.logger.info(f"{'='*80}\n")
        
        return top_stocks
    
    def get_top_stocks_combined(self, top_n: int = 3, min_volume: int = 10000, min_momentum: float = 0.0) -> List[Tuple[str, Dict, float]]:
        """
        Get top N stocks using combined scoring (volume + price momentum)
        
        Args:
            top_n: Number of top stocks to return
            min_volume: Minimum volume threshold
            min_momentum: Minimum % change threshold (default 0.0, can be negative to include losers)
            
        Returns:
            List of tuples: [(symbol, stock_data, score), ...]
        """
        if not self.stock_data:
            self.logger.warning("No stock data available.")
            return []
        
        # Filter by minimum volume and positive momentum (optional)
        filtered = {
            symbol: data 
            for symbol, data in self.stock_data.items() 
            if data.get('volume', 0) >= min_volume and data.get('pct_change', 0) >= min_momentum
        }
        
        if not filtered:
            self.logger.warning(f"No stocks with volume >= {min_volume}")
            return []
        
        # Calculate combined score: (normalized_volume * 0.6) + (normalized_change * 0.4)
        volumes = [d['volume'] for d in filtered.values()]
        max_volume = max(volumes) if volumes else 1
        
        changes = [d.get('pct_change', 0) for d in filtered.values()]
        max_change = max(changes) if changes else 1
        min_change = min(changes) if changes else 0
        change_range = max_change - min_change if max_change != min_change else 1
        
        scored_stocks = []
        
        for symbol, data in filtered.items():
            norm_volume = data['volume'] / max_volume if max_volume > 0 else 0
            norm_change = (data.get('pct_change', 0) - min_change) / change_range if change_range > 0 else 0
            
            score = (norm_volume * 0.6) + (norm_change * 0.4)
            scored_stocks.append((symbol, data, score))
        
        # Sort by score descending
        scored_stocks.sort(key=lambda x: x[2], reverse=True)
        
        top_stocks = scored_stocks[:top_n]
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"TOP {top_n} TRENDING STOCKS (Combined Score)")
        self.logger.info(f"Score = (Volume Rank * 60%) + (Price Momentum * 40%)")
        self.logger.info(f"{'='*80}")
        
        for i, (symbol, data, score) in enumerate(top_stocks, 1):
            self.logger.info(
                f"{i}. {symbol} (Score: {score:.3f}) | "
                f"Volume: {data['volume']:,} | "
                f"Price: Rs. {data['ltp']:.2f} | Change: {data['pct_change']:+.2f}%"
            )
        
        self.logger.info(f"{'='*80}\n")
        
        self.analysis_results = {'type': 'combined', 'stocks': top_stocks}
        return top_stocks
    
    def generate_analysis_report(self) -> str:
        """Generate a detailed analysis report of current market trends"""
        if not self.stock_data:
            return "No market data available"
        
        df = pd.DataFrame.from_dict(self.stock_data, orient='index')
        
        report = "\n" + "="*80 + "\n"
        report += "                    MARKET ANALYSIS REPORT\n"
        report += "="*80 + "\n\n"
        
        report += f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Total Stocks Analyzed: {len(df)}\n"
        report += f"Data Source: {df['source'].iloc[0] if len(df) > 0 else 'N/A'}\n\n"
        
        report += "MARKET STATISTICS:\n"
        report += "-" * 80 + "\n"
        report += f"Total Trading Volume: {df['volume'].sum():,.0f} shares\n"
        report += f"Average Volume per Stock: {df['volume'].mean():,.0f} shares\n"
        report += f"Median Volume per Stock: {df['volume'].median():,.0f} shares\n"
        report += f"Max Volume: {df['volume'].max():,.0f} shares ({df.loc[df['volume'].idxmax(), 'symbol']})\n\n"
        
        report += "PRICE CHANGES:\n"
        report += "-" * 80 + "\n"
        report += f"Gainers: {len(df[df['pct_change'] > 0])} stocks\n"
        report += f"Losers: {len(df[df['pct_change'] < 0])} stocks\n"
        report += f"Unchanged: {len(df[df['pct_change'] == 0])} stocks\n"
        report += f"Highest Gain: {df['pct_change'].max():+.2f}% ({df.loc[df['pct_change'].idxmax(), 'symbol']})\n"
        report += f"Biggest Loss: {df['pct_change'].min():+.2f}% ({df.loc[df['pct_change'].idxmin(), 'symbol']})\n"
        report += f"Average Change: {df['pct_change'].mean():+.2f}%\n\n"
        
        report += "="*80 + "\n"
        
        return report
    
    def print_summary(self):
        """Print a summary of current market data"""
        if not self.stock_data:
            self.logger.info("No market data available")
            return
        
        self.logger.info(self.generate_analysis_report())
        
        # Top 5 by volume
        top_volume = self.get_top_stocks_by_volume(top_n=5)
        
        # Top 5 gainers
        top_gainers = self.get_top_stocks_by_price_change(top_n=5)

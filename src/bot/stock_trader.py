"""
Generic Stock Paper Trading Scheduler
Works with any stock symbol (NABIL, GUFL, etc.)
"""
import schedule
import time
import logging
import os
import json
import re
from datetime import datetime
from typing import Optional, Dict
import random
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

from .trailing_stop_strategy import TrailingStopStrategy
from .paper_trader import PaperTrader
from .logger import setup_logger
from .position_store import delete_position, load_position, save_position
from .trade_history import record_trade
from .notification import send_email_notification


class StockPaperTrader:
    """Generic paper trader for any stock symbol"""
    
    def __init__(self, symbol: str = "NABIL", check_interval: int = 900, log_file: str = None, positions_db_path: str = None):
        """
        Initialize stock paper trader
        
        Args:
            symbol: Stock symbol (e.g., "NABIL", "GUFL") - default NABIL
            check_interval: Check price every N seconds (default 900 = 15 minutes)
            log_file: Log file path (default logs/{symbol}.log)
            positions_db_path: SQLite database used to persist position state
        """
        self.symbol = symbol.upper()
        self.check_interval = check_interval
        self.positions_db_path = positions_db_path or os.getenv("POSITIONS_DB_PATH", "data/nepse_positions.db")
        self.log_file = log_file or f"logs/{self.symbol.lower()}.log"
        self.position_state_file = self.positions_db_path
        
        # Create logger
        self.logger = setup_logger(f"{__name__}.{self.symbol}", log_file=self.log_file)
        
        # Paper trader
        self.paper_trader = PaperTrader(logger=self.logger)
        
        # Strategy
        self.strategy: Optional[TrailingStopStrategy] = None
        
        # Price data
        self.current_price = None
        self.price_history = []
        
        # Control flags
        self.running = False
        self.trades_count = 0
        self.checks_count = 0
        # Track last persisted stop loss to persist changes only when they occur
        self.last_stop_loss = None
        # Ensure we only alert once per stop-loss trigger until position changes
        self.stoploss_alerted = False
        
        self.logger.info(f"{self.symbol} Paper Trader initialized - Check interval: {check_interval} seconds")

        self.logger.info("\n" + "="*90)
        self.logger.info(f"{self.symbol} PAPER TRADING STARTED")
        self.logger.info(f"Log File: {self.log_file}")
        self.logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Check Interval: {self.check_interval} seconds")
        self.logger.info("="*90 + "\n")
    
    def setup_strategy(self, entry_price: float = None, initial_quantity: int = 10, existing_position: Dict = None):
        """Setup trading strategy"""
        if existing_position:
            try:
                existing_quantity = int(existing_position["shares"])
                existing_avg_cost = float(existing_position["avg_cost"])
            except (KeyError, TypeError, ValueError) as e:
                raise ValueError("Invalid existing position data") from e

            if existing_quantity <= 0:
                raise ValueError("Existing position must have at least one share")

            self.logger.info(f">>> RESTORING EXISTING POSITION FOR {self.symbol}")
            self.logger.info(f"    Existing Quantity: {existing_quantity} shares")
            self.logger.info(f"    Entry Price (Stored): Rs. {existing_avg_cost:.2f}\n")

            self.current_price = existing_position.get("current_price", existing_avg_cost)
            self.price_history = [existing_avg_cost]

            if "cash" in existing_position:
                try:
                    self.paper_trader.cash = float(existing_position["cash"])
                except (TypeError, ValueError):
                    pass

            self.paper_trader.seed_position(
                symbol=self.symbol,
                quantity=existing_quantity,
                avg_cost=existing_avg_cost,
                total_invested=existing_position.get("total_invested")
            )

            self.strategy = TrailingStopStrategy(
                trader=self.paper_trader,
                symbol=self.symbol,
                initial_quantity=existing_quantity,
                entry_price=existing_avg_cost,
                stop_loss_pct=10,
                trailing_activation_pct=10,
                trailing_step_pct=5,
                ladder_triggers={20: 20, 30: 10}
            )
            self.strategy.seed_position(existing_quantity, existing_avg_cost)
            self.last_stop_loss = self.strategy.current_stop_loss

            self.logger.info(f">>> EXISTING POSITION READY - STRATEGY WILL USE RS. {existing_avg_cost:.2f} AS THE REFERENCE PRICE\n")
            return

        # Always fetch from live NEPSE if price not provided
        if not entry_price or entry_price == 0:
            self.logger.info(f"\n>>> FETCHING REAL {self.symbol} PRICE FROM SHARESANSAR...")
            try:
                entry_price = self.fetch_real_price()
                self.logger.info(f"    Entry Price (ShareSansar Live): Rs. {entry_price:.2f}\n")
            except Exception as e:
                self.logger.error(f"\n✗ Unable to fetch live price from ShareSansar: {str(e)}")
                self.logger.error(f"\nYou must provide the {self.symbol} price manually:")
                self.logger.error(f"  1. Visit https://www.sharesansar.com/live-trading")
                self.logger.error(f"  2. Find {self.symbol} price in the live trading table")
                self.logger.error(f"  3. Run: trader.setup_strategy(entry_price=YOUR_PRICE)")
                raise ValueError(f"Failed to fetch {self.symbol} price and none provided manually") from e
        
        self.logger.info(f">>> SETTING UP STRATEGY FOR {self.symbol}")
        self.logger.info(f"    Entry Price (Live): Rs. {entry_price:.2f}")
        self.logger.info(f"    Initial Quantity: {initial_quantity} shares\n")
        
        # Set initial price
        self.current_price = entry_price
        self.price_history = [self.current_price]
        
        # Setup strategy
        self.strategy = TrailingStopStrategy(
            trader=self.paper_trader,
            symbol=self.symbol,
            initial_quantity=initial_quantity,
            entry_price=entry_price,
            stop_loss_pct=10,
            trailing_activation_pct=10,
            trailing_step_pct=5,
            ladder_triggers={20: 20, 30: 10}
        )
        
        # Execute initial buy
        self.logger.info(f">>> EXECUTING INITIAL BUY ORDER")
        initial_order = self.strategy.create_initial_order()
        result = self.paper_trader.place_buy_order(
            symbol=self.symbol,
            quantity=initial_quantity,
            price=entry_price
        )
        
        if result['success']:
            self.strategy.execute_order(initial_order, entry_price)
            self.trades_count += 1
            self.last_stop_loss = self.strategy.current_stop_loss

    def load_position_state(self) -> Optional[Dict]:
        """Load a previously saved open position from the SQLite store."""
        state = load_position(self.symbol, positions_dir=self.positions_db_path)
        if not state:
            return None
        if state.get("symbol") != self.symbol:
            return None
        if int(state.get("shares", 0)) <= 0:
            return None
        return state

    def save_position_state(self):
        """Persist the current open position so trading can resume later."""
        position = self.paper_trader.get_position(self.symbol)

        if not position or position.get("shares", 0) <= 0:
            delete_position(self.symbol, positions_dir=self.positions_db_path)
            # Reset stoploss alert tracking when position is removed
            self.last_stop_loss = None
            self.stoploss_alerted = False
            return

        state = {
            "symbol": self.symbol,
            "shares": position["shares"],
            "avg_cost": position["avg_cost"],
            "total_invested": position["total_invested"],
            "cash": self.paper_trader.cash,
            "current_price": self.current_price,
            "entry_price": self.strategy.entry_price if self.strategy else position["avg_cost"],
            "stop_loss": self.strategy.current_stop_loss if self.strategy else None,
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        save_position(state, positions_dir=self.positions_db_path)
        self.logger.info(f"Saved open position to SQLite DB {self.positions_db_path}")

    def _has_open_position(self) -> bool:
        """Return True if the trader still holds shares for this symbol."""
        position = self.paper_trader.get_position(self.symbol)
        return bool(position and int(position.get("shares", 0)) > 0)

    def _deactivate_closed_position(self):
        """Clear in-memory strategy state once the position has been fully closed."""
        self.strategy = None
        self.last_stop_loss = None
        self.stoploss_alerted = False
        self.current_price = None
        self.price_history = []
        self.logger.info(f"{self.symbol} monitoring stopped - position fully closed")
    
    def fetch_real_price(self) -> float:
        """Fetch real stock price from sharesansar.com/live-trading"""
        try:
            url = "https://www.sharesansar.com/live-trading"
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all('td')
                    
                    if len(cells) >= 3:
                        try:
                            # Column structure: S.No | Symbol | LTP | Point Change | % Change | Open | High | Low | Volume | Prev. Close
                            # Symbol is typically in column 1 (index 1)
                            symbol_cell = cells[1].get_text(strip=True)
                            symbol = ''.join(c for c in symbol_cell if c.isalpha()).upper()
                            
                            if symbol == self.symbol:
                                # LTP is in column 2 (index 2)
                                price_cell = cells[2].get_text(strip=True)
                                price_str = price_cell.replace(',', '').split()[0]
                                price = float(price_str)
                                
                                if 10 < price < 100000:  # Valid price range for NEPSE stocks
                                    self.logger.info(f"✓ {self.symbol} Price from ShareSansar (Live): Rs. {price:.2f}")
                                    return price
                        except (ValueError, IndexError, AttributeError):
                            continue
            
            # Fallback text search for symbol in page
            self.logger.debug("Table parsing inconclusive, trying text search...")
            page_text = soup.get_text()
            
            # Find symbol followed by price pattern
            pattern = rf"{self.symbol}\s+(\d+(?:\.\d+)?)"
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            
            if matches:
                try:
                    price = float(matches[0])
                    if 10 < price < 100000:
                        self.logger.info(f"✓ {self.symbol} Price from ShareSansar (text): Rs. {price:.2f}")
                        return price
                except (ValueError, IndexError):
                    pass
            
            raise ValueError(f"{self.symbol} price not found in ShareSansar live trading data")
            
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Cannot connect to sharesansar.com: {str(e)}")
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Request to sharesansar.com timed out: {str(e)}")
        except Exception as e:
            raise Exception(f"Error fetching {self.symbol} price from ShareSansar: {str(e)}")
    
    def simulate_price_movement(self):
        """Get next price - tries real price, falls back to simulation"""
        try:
            real_price = self.fetch_real_price()
            return real_price
        except Exception as e:
            self.logger.debug(f"Real price fetch failed, using simulated: {str(e)}")
            return self.simulate_price_fallback()
    
    def simulate_price_fallback(self) -> float:
        """Fallback price simulation"""
        if self.current_price is None:
            raise ValueError("Cannot simulate - strategy not initialized")
        
        change_pct = random.uniform(-0.5, 0.5) / 100
        new_price = self.current_price * (1 + change_pct)
        
        min_price = self.strategy.entry_price * 0.7 if self.strategy else self.current_price * 0.7
        max_price = self.strategy.entry_price * 1.5 if self.strategy else self.current_price * 1.5
        new_price = max(min_price, min(max_price, new_price))
        
        return new_price
    
    def check_price_and_execute(self):
        """Called every N seconds - checks price and executes orders"""
        if not self.strategy:
            return

        if not self._has_open_position():
            self.save_position_state()
            self._deactivate_closed_position()
            return
        
        self.checks_count += 1
        
        self.current_price = self.simulate_price_movement()
        self.price_history.append(self.current_price)
        
        self.logger.info(
            f"\n[CHECK #{self.checks_count:04d}] {datetime.now().strftime('%H:%M:%S')} "
            f"| Price: Rs. {self.current_price:.2f}"
        )

        # First run strategy analysis so it can update trailing stop state
        pending_orders = self.strategy.analyze(self.current_price) if self.strategy else []

        # Log stop loss and profit information (use updated strategy state)
        if self.strategy:
            entry_price = self.strategy._get_average_entry_price()
            stop_loss_level = self.strategy.current_stop_loss
            stop_loss_pct = self.strategy.stop_loss_pct

            # Calculate profit guarantee point (use stop_loss_pct as reference for symmetry)
            profit_guarantee_level = entry_price * (1 + stop_loss_pct / 100)

            distance_to_sl = self.current_price - stop_loss_level
            distance_to_profit = profit_guarantee_level - self.current_price

            self.logger.info(f"\n>>> STOP LOSS & PROFIT STATUS:")
            self.logger.info(f"    Entry Price:           Rs. {entry_price:.2f}")
            self.logger.info(f"    Current Price:         Rs. {self.current_price:.2f}")
            self.logger.info(f"    Current Stop Loss:     Rs. {stop_loss_level:.2f} ({stop_loss_pct:.1f}% below entry)")
            self.logger.info(f"    Distance to Stop Loss: Rs. {distance_to_sl:.2f}")
            if distance_to_sl <= 0:
                self.logger.warning(f"    ⚠️  STOP LOSS WILL TRIGGER! ({-distance_to_sl:.2f} Rs below stop level)")
                if not self.stoploss_alerted:
                    subject = f"STOP-LOSS ALERT: {self.symbol} @ Rs. {self.current_price:.2f}"
                    body = (
                        f"Stop loss has been hit for {self.symbol}.\n\n"
                        f"Entry Price: Rs. {entry_price:.2f}\n"
                        f"Current Price: Rs. {self.current_price:.2f}\n"
                        f"Stop Loss: Rs. {stop_loss_level:.2f}\n"
                        f"Shares: {self.strategy.total_quantity}\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )
                    sent = send_email_notification(subject, body, logger=self.logger)
                    if sent:
                        self.logger.info("Sent stop-loss email notification")
                    else:
                        self.logger.warning(
                            "Stop-loss email not sent. Check EMAIL_SMTP, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, EMAIL_TO and Gmail app password."
                        )
                    self.stoploss_alerted = True
            self.logger.info(f"    Guaranteed Profit Level: Rs. {profit_guarantee_level:.2f}")
            self.logger.info(f"    Distance to Profit:      Rs. {distance_to_profit:.2f}")

            position_pct = self.strategy._calculate_position_pct_change()
            self.logger.info(f"    Current Position P&L:    {position_pct:+.2f}%\n")

            # Notify when trailing stop has moved up to a new level
            try:
                current_stop_loss = float(stop_loss_level)
            except (TypeError, ValueError):
                current_stop_loss = None

            if current_stop_loss is not None:
                previous_stop_loss = self.last_stop_loss
                if previous_stop_loss is None:
                    self.last_stop_loss = current_stop_loss
                elif current_stop_loss > previous_stop_loss + 1e-9:
                    subject = f"STOP-LOSS UPDATED: {self.symbol} @ Rs. {current_stop_loss:.2f}"
                    body = (
                        f"Trailing stop updated for {self.symbol}.\n\n"
                        f"Entry Price: Rs. {entry_price:.2f}\n"
                        f"Current Price: Rs. {self.current_price:.2f}\n"
                        f"Old Stop Loss: Rs. {previous_stop_loss:.2f}\n"
                        f"New Stop Loss: Rs. {current_stop_loss:.2f}\n"
                        f"Shares: {self.strategy.total_quantity}\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )
                    sent = send_email_notification(subject, body, logger=self.logger)
                    if sent:
                        self.logger.info(
                            f"Sent stop-loss update email: Rs. {previous_stop_loss:.2f} -> Rs. {current_stop_loss:.2f}"
                        )
                    else:
                        self.logger.warning(
                            "Stop-loss update email not sent. Check EMAIL_SMTP, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, EMAIL_TO and Gmail app password."
                        )
                    self.last_stop_loss = current_stop_loss

                    try:
                        self.save_position_state()
                    except Exception:
                        self.logger.exception("Failed to persist updated stop loss")
        
        if pending_orders:
            self.logger.info(f">>> {len(pending_orders)} ORDER(S) TRIGGERED - EXECUTING AUTOMATICALLY\n")
            
            for order in pending_orders:
                self.logger.info(f"\n{self.strategy.get_order_summary(pending_orders)}")
                
                if order.order_type.value.startswith("BUY"):
                    result = self.paper_trader.place_buy_order(
                        symbol=self.symbol,
                        quantity=order.quantity,
                        price=self.current_price
                    )
                elif order.order_type.value.startswith("SELL"):
                    result = self.paper_trader.place_sell_order(
                        symbol=self.symbol,
                        quantity=order.quantity,
                        price=self.current_price
                    )
                    
                    # Record completed trade to trade history
                    if result.get('success'):
                        buy_price = result.get('avg_cost', self.current_price)
                        # Get buy price from strategy or paper trader
                        if self.strategy:
                            buy_price = self.strategy.entry_price
                        record_trade(
                            symbol=self.symbol,
                            quantity=order.quantity,
                            buy_price=buy_price,
                            sell_price=self.current_price,
                            pnl=result.get('pnl', 0),
                            pnl_pct=result.get('pnl_pct', 0),
                            sell_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )
                
                if result['success']:
                    self.strategy.execute_order(order, self.current_price)
                    self.trades_count += 1

                    # If this was a full sell, stop monitoring this symbol immediately.
                    if order.order_type.value.startswith("SELL") and not self._has_open_position():
                        self.save_position_state()
                        self._deactivate_closed_position()
                        return
        
        if self.checks_count % 10 == 0:
            self.paper_trader.log_summary({self.symbol: self.current_price})
    
    def start(self, duration_minutes: int = None):
        """Start paper trading"""
        if not self.strategy:
            self.logger.error("Strategy not setup. Call setup_strategy() first.")
            return
        
        self.running = True
        
        self.logger.info(f"\n{'='*90}")
        self.logger.info(f"STARTING AUTOMATED PAPER TRADING FOR {self.symbol}")
        if duration_minutes:
            self.logger.info(f"Duration: {duration_minutes} minutes")
        else:
            self.logger.info(f"Duration: CONTINUOUS (runs indefinitely until Ctrl+C)")
        self.logger.info(f"Check interval: {self.check_interval} seconds")
        self.logger.info(f"{'='*90}\n")
        
        schedule.every(self.check_interval).seconds.do(self.check_price_and_execute)
        
        start_time = time.time()
        duration_seconds = (duration_minutes * 60) if duration_minutes else float('inf')
        
        try:
            while time.time() - start_time < duration_seconds and self.running:
                schedule.run_pending()
                time.sleep(1)
        
        except KeyboardInterrupt:
            self.logger.info("\n\n>>> STOPPED BY USER")
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop trading and generate report"""
        self.running = False
        schedule.clear()

        self.save_position_state()
        
        self.logger.info(f"\n{'='*90}")
        self.logger.info(f"{self.symbol} PAPER TRADING STOPPED")
        self.logger.info(f"{'='*90}\n")
        
        final_report = self.paper_trader.generate_report({self.symbol: self.current_price})
        self.logger.info(final_report)
        
        self.logger.info(f"\nFINAL STATISTICS:")
        self.logger.info(f"  Total Checks: {self.checks_count}")
        self.logger.info(f"  Total Trades: {self.trades_count}")
        self.logger.info(f"  Final Price: Rs. {self.current_price:.2f}")
        if self.price_history:
            self.logger.info(f"  Price Change: {((self.current_price - self.price_history[0]) / self.price_history[0] * 100):+.2f}%")
        self.logger.info(f"\n{'='*90}\n")
    
    def get_status(self) -> Dict:
        """Get current trading status"""
        if not self.strategy:
            return {'status': 'Not started'}
        
        portfolio = self.paper_trader.get_portfolio_value({self.symbol: self.current_price})
        bought_price = self.strategy.entry_price if self.strategy else None
        profit_loss = portfolio['total_unrealized_pnl']
        
        return {
            'symbol': self.symbol,
            'checks': self.checks_count,
            'trades': self.trades_count,
            'bought_price': bought_price,
            'current_price': self.current_price,
            'profit_loss': profit_loss,
            'unrealized_pnl': profit_loss,
            'portfolio_value': portfolio['total_value'],
            'position': self.strategy.total_quantity,
            'running': self.running
        }


# Backward compatibility - NABIL alias
class NABILPaperTrader(StockPaperTrader):
    """NABIL-specific trader (uses generic StockPaperTrader with NABIL symbol)"""
    
    def __init__(self, check_interval: int = 900, log_file: str = "logs/nabil.log"):
        super().__init__(symbol="NABIL", check_interval=check_interval, log_file=log_file)


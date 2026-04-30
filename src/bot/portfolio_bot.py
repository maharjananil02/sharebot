"""
Portfolio bot manager.

Runs one or more StockPaperTrader instances against saved JSON positions.
This is designed for Streamlit so the UI can start/stop a background monitor
without relying on the global schedule loop.
"""
from __future__ import annotations

import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

import os

from .logger import setup_logger
from .position_store import list_positions
from .stock_trader import StockPaperTrader

logger = setup_logger(__name__)


class PortfolioBotManager:
    """Monitor one or more saved positions with auto bot logic."""

    def __init__(self, positions_db_path: str = None, check_interval_seconds: int = 900):
        self.positions_db_path = positions_db_path or os.getenv("POSITIONS_DB_PATH", "data/nepse_positions.db")
        self.check_interval_seconds = int(check_interval_seconds)
        self.logger = logger
        self.traders: Dict[str, StockPaperTrader] = {}
        self.running = False
        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None
        self.last_run_at: Optional[str] = None
        # When True, suppress saving positions on shutdown (used for safe deletes)
        self.suppress_save_on_stop = False

    def load_traders(self, force: bool = False) -> Dict[str, StockPaperTrader]:
        """Load traders from saved JSON positions."""
        if self.traders and not force:
            return self.traders

        self.traders = {}
        positions = list_positions(self.positions_db_path)

        for position in positions:
            symbol = str(position.get("symbol", "")).upper()
            if not symbol:
                continue

            try:
                trader = StockPaperTrader(
                    symbol=symbol,
                    check_interval=self.check_interval_seconds,
                    positions_db_path=self.positions_db_path,
                    log_file=f"logs/{symbol.lower()}_bot.log",
                )
                trader.setup_strategy(existing_position=position)
                self.traders[symbol] = trader
                self.logger.info(f"Loaded bot for {symbol}")
            except Exception as exc:
                self.logger.error(f"Failed to load trader for {symbol}: {exc}")

        return self.traders

    def tick(self):
        """Run one monitoring cycle for all loaded traders."""
        if not self.traders:
            self.load_traders()

        for symbol, trader in self.traders.items():
            try:
                trader.check_price_and_execute()
                trader.save_position_state()
            except Exception as exc:
                self.logger.error(f"Error updating {symbol}: {exc}")

        self.last_run_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def start(self):
        """Run the bot loop until stop() is called."""
        if self.running:
            return

        self.running = True
        self.stop_event.clear()

        if not self.traders:
            self.load_traders()

        self.logger.info("Starting portfolio bot manager")

        try:
            while not self.stop_event.is_set():
                cycle_start = time.time()
                self.tick()
                elapsed = time.time() - cycle_start
                wait_seconds = max(1, self.check_interval_seconds - elapsed)
                self.stop_event.wait(wait_seconds)
        finally:
            self.running = False
            self.stop_event.clear()
            # Persist positions unless suppression was requested.
            if not getattr(self, "suppress_save_on_stop", False):
                self.save_all_positions()
            # Reset suppression after shutdown
            self.suppress_save_on_stop = False
            self.logger.info("Portfolio bot manager stopped")

    def start_background(self):
        """Start the bot in a background thread."""
        if self.thread and self.thread.is_alive():
            return self.thread

        self.thread = threading.Thread(target=self.start, daemon=True)
        self.thread.start()
        return self.thread

    def stop(self):
        """Signal the bot loop to stop."""
        # Default stop will request the loop to end. The loop's finally block
        # is responsible for persisting positions unless suppressed.
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=max(1, int(self.check_interval_seconds)))
        # Do not call save_all_positions here — the background thread's finally
        # handles saving and respects `suppress_save_on_stop`.

    def stop(self, suppress_save: bool = False):
        """Signal the bot loop to stop.

        If `suppress_save` is True, the manager will not persist trader positions
        when shutting down. This is useful when removing a position file to
        avoid the bot re-creating it while stopping.
        """
        self.suppress_save_on_stop = bool(suppress_save)
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=max(1, int(self.check_interval_seconds)))
        # Reset suppression flag after stop to avoid affecting future runs.
        self.suppress_save_on_stop = False

    def save_all_positions(self):
        """Persist all trader positions to JSON."""
        for trader in self.traders.values():
            try:
                trader.save_position_state()
            except Exception as exc:
                self.logger.error(f"Failed to save position for {trader.symbol}: {exc}")

    def get_status(self) -> List[Dict]:
        """Return current status for all traders."""
        status_rows: List[Dict] = []
        for symbol, trader in self.traders.items():
            try:
                status = trader.get_status()
                status_rows.append(status)
            except Exception as exc:
                status_rows.append({
                    "symbol": symbol,
                    "status": f"error: {exc}",
                    "running": self.running,
                })
        return status_rows

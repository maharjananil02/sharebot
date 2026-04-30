"""
Position storage helpers for Streamlit and paper trading.

Stores open positions as JSON files that match the GUFL position format:
{
  symbol, shares, avg_cost, total_invested, cash, current_price, entry_price, saved_at
}
"""
from __future__ import annotations

import glob
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

DEFAULT_LOGS_DIR = "logs"


def _normalize_symbol(symbol: str) -> str:
    if not symbol:
        raise ValueError("Symbol is required")
    return symbol.strip().upper()


def get_position_file_path(symbol: str, logs_dir: str = DEFAULT_LOGS_DIR) -> str:
    """Return the JSON path used to persist a symbol position."""
    symbol = _normalize_symbol(symbol)
    os.makedirs(logs_dir, exist_ok=True)
    return os.path.join(logs_dir, f"{symbol.lower()}_position.json")


def build_position_record(
    symbol: str,
    shares: int,
    avg_cost: float,
    total_invested: Optional[float] = None,
    cash: float = 1000000,
    current_price: Optional[float] = None,
    entry_price: Optional[float] = None,
    saved_at: Optional[str] = None,
    **extra_fields,
) -> Dict:
    """Build a position dictionary in the same format as gufl_position.json."""
    symbol = _normalize_symbol(symbol)
    shares = int(shares)
    avg_cost = float(avg_cost)

    if shares < 0:
        raise ValueError("Shares cannot be negative")
    if avg_cost < 0:
        raise ValueError("Average cost cannot be negative")

    if total_invested is None:
        total_invested = shares * avg_cost

    if current_price is None:
        current_price = avg_cost
    if entry_price is None:
        entry_price = avg_cost
    if saved_at is None:
        saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    record = {
        "symbol": symbol,
        "shares": shares,
        "avg_cost": avg_cost,
        "total_invested": float(total_invested),
        "cash": float(cash),
        "current_price": float(current_price),
        "entry_price": float(entry_price),
        "saved_at": saved_at,
    }
    record.update(extra_fields)
    return record


def save_position(position: Dict, logs_dir: str = DEFAULT_LOGS_DIR) -> str:
    """Save a position dictionary to disk and return the file path."""
    symbol = _normalize_symbol(position.get("symbol"))
    path = get_position_file_path(symbol, logs_dir=logs_dir)

    position_to_save = dict(position)
    position_to_save["symbol"] = symbol
    position_to_save.setdefault("saved_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    with open(path, "w", encoding="utf-8") as file:
        json.dump(position_to_save, file, indent=2)

    return path


def load_position(symbol: str, logs_dir: str = DEFAULT_LOGS_DIR) -> Optional[Dict]:
    """Load a saved position for a symbol, if it exists."""
    path = get_position_file_path(symbol, logs_dir=logs_dir)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None

    if not data.get("symbol"):
        return None
    return data


def list_positions(logs_dir: str = DEFAULT_LOGS_DIR) -> List[Dict]:
    """Return all saved positions in the logs directory."""
    positions: List[Dict] = []
    pattern = os.path.join(logs_dir, "*_position.json")

    for path in sorted(glob.glob(pattern)):
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if data.get("symbol") and int(data.get("shares", 0)) > 0:
                data["file_path"] = path
                positions.append(data)
        except (OSError, json.JSONDecodeError, ValueError, TypeError):
            continue

    return positions


def delete_position(symbol: str, logs_dir: str = DEFAULT_LOGS_DIR) -> bool:
    """Delete a saved position file."""
    # Remove position JSON
    path = get_position_file_path(symbol, logs_dir=logs_dir)
    # Also attempt to remove associated bot log file
    log_path = os.path.join(logs_dir, f"{_normalize_symbol(symbol).lower()}_bot.log")

    removed_any = False

    if os.path.exists(path):
        try:
            os.remove(path)
            removed_any = True
        except OSError:
            pass

    if os.path.exists(log_path):
        try:
            os.remove(log_path)
            removed_any = True
        except OSError:
            pass

    return removed_any

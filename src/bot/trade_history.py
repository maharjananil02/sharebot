"""
Trade history manager - tracks and persists completed trades (sells).

Stores completed trades as JSON files that record each sale transaction.
"""
from __future__ import annotations

import glob
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

DEFAULT_LOGS_DIR = "logs"
TRADE_HISTORY_FILE = os.path.join(DEFAULT_LOGS_DIR, "completed_trades.json")


def ensure_trade_history_file(logs_dir: str = DEFAULT_LOGS_DIR) -> str:
    """Ensure the trade history file exists."""
    os.makedirs(logs_dir, exist_ok=True)
    history_file = os.path.join(logs_dir, "completed_trades.json")
    if not os.path.exists(history_file):
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump({"trades": []}, f, indent=2)
    return history_file


def record_trade(
    symbol: str,
    quantity: int,
    buy_price: float,
    sell_price: float,
    pnl: float,
    pnl_pct: float,
    sell_timestamp: Optional[str] = None,
    logs_dir: str = DEFAULT_LOGS_DIR,
) -> Dict:
    """Record a completed trade (sale) to history."""
    if sell_timestamp is None:
        sell_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    history_file = ensure_trade_history_file(logs_dir)
    
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        data = {"trades": []}
    
    trade_record = {
        "symbol": symbol.upper(),
        "quantity": int(quantity),
        "buy_price": float(buy_price),
        "sell_price": float(sell_price),
        "pnl": float(pnl),
        "pnl_pct": float(pnl_pct),
        "total_invested": int(quantity) * float(buy_price),
        "total_proceeds": int(quantity) * float(sell_price),
        "sold_at": sell_timestamp,
    }
    
    data["trades"].append(trade_record)
    
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    return trade_record


def get_trade_history(logs_dir: str = DEFAULT_LOGS_DIR) -> List[Dict]:
    """Get all completed trades sorted by timestamp (newest first)."""
    history_file = ensure_trade_history_file(logs_dir)
    
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    
    trades = data.get("trades", [])
    # Sort by sold_at timestamp (newest first)
    return sorted(trades, key=lambda x: x.get("sold_at", ""), reverse=True)


def get_trades_by_symbol(symbol: str, logs_dir: str = DEFAULT_LOGS_DIR) -> List[Dict]:
    """Get all completed trades for a specific symbol."""
    all_trades = get_trade_history(logs_dir)
    return [t for t in all_trades if t.get("symbol") == symbol.upper()]


def get_trade_statistics(logs_dir: str = DEFAULT_LOGS_DIR) -> Dict:
    """Get overall trade statistics."""
    trades = get_trade_history(logs_dir)
    
    if not trades:
        return {
            "total_trades": 0,
            "total_profit": 0.0,
            "total_loss": 0.0,
            "total_pnl": 0.0,
            "win_rate": 0.0,
            "avg_pnl_pct": 0.0,
            "total_quantity_sold": 0,
        }
    
    profitable_trades = [t for t in trades if t["pnl"] > 0]
    losing_trades = [t for t in trades if t["pnl"] < 0]
    
    total_profit = sum(t["pnl"] for t in profitable_trades)
    total_loss = sum(abs(t["pnl"]) for t in losing_trades)
    total_pnl = sum(t["pnl"] for t in trades)
    
    return {
        "total_trades": len(trades),
        "profitable_trades": len(profitable_trades),
        "losing_trades": len(losing_trades),
        "total_profit": float(total_profit),
        "total_loss": float(total_loss),
        "total_pnl": float(total_pnl),
        "win_rate": (len(profitable_trades) / len(trades) * 100) if trades else 0.0,
        "avg_pnl_pct": (sum(t["pnl_pct"] for t in trades) / len(trades)) if trades else 0.0,
        "total_quantity_sold": sum(t["quantity"] for t in trades),
    }


def clear_trade_history(logs_dir: str = DEFAULT_LOGS_DIR) -> bool:
    """Clear all trade history."""
    history_file = ensure_trade_history_file(logs_dir)
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump({"trades": []}, f, indent=2)
        return True
    except OSError:
        return False

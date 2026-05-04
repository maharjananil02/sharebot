"""Trade history manager - tracks and persists completed trades using SQLite."""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

DEFAULT_TRADES_DB = os.getenv("TRADES_DB_PATH", "data/trades.db")


def _resolve_db_path(db_path: Optional[str] = None) -> str:
    """Resolve and initialize trade history database path."""
    resolved = (db_path or DEFAULT_TRADES_DB).strip()
    
    if resolved.endswith((".db", ".sqlite", ".sqlite3")):
        db_file = resolved
    else:
        db_file = os.path.join(resolved, "trades.db")
    
    parent_dir = os.path.dirname(db_file)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    return db_file


def _get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Get SQLite connection and initialize schema."""
    db_file = _resolve_db_path(db_path)
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            buy_price REAL NOT NULL,
            sell_price REAL NOT NULL,
            pnl REAL NOT NULL,
            pnl_pct REAL NOT NULL,
            total_invested REAL NOT NULL,
            total_proceeds REAL NOT NULL,
            sold_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def record_trade(
    symbol: str,
    quantity: int,
    buy_price: float,
    sell_price: float,
    pnl: float,
    pnl_pct: float,
    sell_timestamp: Optional[str] = None,
    logs_dir: str = None,
) -> Dict:
    """Record a completed trade (sale) to SQLite history."""
    if sell_timestamp is None:
        sell_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
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
    
    with _get_connection(logs_dir) as conn:
        conn.execute(
            """
            INSERT INTO trades (
                symbol, quantity, buy_price, sell_price, pnl, pnl_pct,
                total_invested, total_proceeds, sold_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trade_record["symbol"],
                trade_record["quantity"],
                trade_record["buy_price"],
                trade_record["sell_price"],
                trade_record["pnl"],
                trade_record["pnl_pct"],
                trade_record["total_invested"],
                trade_record["total_proceeds"],
                trade_record["sold_at"],
            ),
        )
        conn.commit()
    
    return trade_record


def get_trade_history(logs_dir: str = None) -> List[Dict]:
    """Get all completed trades sorted by timestamp (newest first)."""
    with _get_connection(logs_dir) as conn:
        rows = conn.execute(
            "SELECT * FROM trades ORDER BY sold_at DESC"
        ).fetchall()
    
    trades = []
    for row in rows:
        trades.append({
            "id": row["id"],
            "symbol": row["symbol"],
            "quantity": int(row["quantity"]),
            "buy_price": float(row["buy_price"]),
            "sell_price": float(row["sell_price"]),
            "pnl": float(row["pnl"]),
            "pnl_pct": float(row["pnl_pct"]),
            "total_invested": float(row["total_invested"]),
            "total_proceeds": float(row["total_proceeds"]),
            "sold_at": row["sold_at"],
        })
    return trades


def get_trades_by_symbol(symbol: str, logs_dir: str = None) -> List[Dict]:
    """Get all completed trades for a specific symbol."""
    with _get_connection(logs_dir) as conn:
        rows = conn.execute(
            "SELECT * FROM trades WHERE symbol = ? ORDER BY sold_at DESC",
            (symbol.upper(),),
        ).fetchall()
    
    trades = []
    for row in rows:
        trades.append({
            "id": row["id"],
            "symbol": row["symbol"],
            "quantity": int(row["quantity"]),
            "buy_price": float(row["buy_price"]),
            "sell_price": float(row["sell_price"]),
            "pnl": float(row["pnl"]),
            "pnl_pct": float(row["pnl_pct"]),
            "total_invested": float(row["total_invested"]),
            "total_proceeds": float(row["total_proceeds"]),
            "sold_at": row["sold_at"],
        })
    return trades


def get_trade_statistics(logs_dir: str = None) -> Dict:
    """Get overall trade statistics."""
    trades = get_trade_history(logs_dir)
    
    if not trades:
        return {
            "total_trades": 0,
            "profitable_trades": 0,
            "losing_trades": 0,
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


def clear_trade_history(logs_dir: str = None) -> bool:
    """Clear all trade history."""
    try:
        with _get_connection(logs_dir) as conn:
            conn.execute("DELETE FROM trades")
            conn.commit()
        return True
    except Exception:
        return False


def migrate_legacy_trades(source_json_path: str = "logs/completed_trades.json", target_db: str = None) -> int:
    """Migrate trades from legacy JSON file to SQLite."""
    if not os.path.exists(source_json_path):
        return 0
    
    migrated_count = 0
    try:
        with open(source_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return 0
    
    trades = data.get("trades", [])
    for trade in trades:
        try:
            record_trade(
                symbol=trade.get("symbol", ""),
                quantity=int(trade.get("quantity", 0)),
                buy_price=float(trade.get("buy_price", 0)),
                sell_price=float(trade.get("sell_price", 0)),
                pnl=float(trade.get("pnl", 0)),
                pnl_pct=float(trade.get("pnl_pct", 0)),
                sell_timestamp=trade.get("sold_at"),
                logs_dir=target_db,
            )
            migrated_count += 1
        except Exception:
            continue
    
    return migrated_count

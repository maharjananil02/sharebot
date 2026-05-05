"""SQLite-backed position storage.

This module stores positions in a SQLite database. The legacy ``positions_dir``
parameter name is kept for backward compatibility with existing call sites.
"""
from __future__ import annotations

import glob
import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


DEFAULT_POSITIONS_TARGET = (
    os.getenv("POSITIONS_DB_PATH")
    or os.getenv("POSITIONS_DIR")
    or "data/positions.db"
)


def _normalize_symbol(symbol: str) -> str:
    if not symbol:
        raise ValueError("Symbol is required")
    return symbol.strip().upper()


def _resolve_db_path(target: Optional[str]) -> str:
    resolved = (target or DEFAULT_POSITIONS_TARGET).strip()

    if resolved.startswith("sqlite:///"):
        db_path = resolved[len("sqlite:///"):]
    else:
        looks_like_file = resolved.endswith((".db", ".sqlite", ".sqlite3"))
        if looks_like_file:
            db_path = resolved
        else:
            db_path = os.path.join(resolved, "positions.db")

    parent_dir = os.path.dirname(db_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    
    # Debug logging
    abs_path = os.path.abspath(db_path)
    exists = os.path.exists(abs_path)
    print(f"[POSITION_STORE] DB Path: {abs_path} | Exists: {exists}")
    
    return db_path


def _get_connection(target: Optional[str] = None) -> sqlite3.Connection:
    db_path = _resolve_db_path(target)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS positions (
            symbol TEXT PRIMARY KEY,
            shares INTEGER NOT NULL,
            avg_cost REAL NOT NULL,
            total_invested REAL NOT NULL,
            cash REAL NOT NULL,
            current_price REAL NOT NULL,
            entry_price REAL NOT NULL,
            saved_at TEXT NOT NULL,
            extra_json TEXT
        )
        """
    )
    conn.commit()
    return conn


def get_position_file_path(symbol: str, positions_dir: Optional[str] = None) -> str:
    symbol = _normalize_symbol(symbol)
    db_path = _resolve_db_path(positions_dir)
    return f"sqlite:///{db_path}#symbol={symbol}"


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
    symbol = _normalize_symbol(symbol)
    shares = int(shares)
    avg_cost = float(avg_cost)
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


def save_position(position: Dict, positions_dir: Optional[str] = None) -> str:
    symbol = _normalize_symbol(position.get("symbol"))
    saved_at = position.get("saved_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    base_fields = {
        "symbol",
        "shares",
        "avg_cost",
        "total_invested",
        "cash",
        "current_price",
        "entry_price",
        "saved_at",
    }
    extra_fields = {k: v for k, v in dict(position).items() if k not in base_fields}

    with _get_connection(positions_dir) as conn:
        conn.execute(
            """
            INSERT INTO positions (
                symbol, shares, avg_cost, total_invested, cash,
                current_price, entry_price, saved_at, extra_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
                shares=excluded.shares,
                avg_cost=excluded.avg_cost,
                total_invested=excluded.total_invested,
                cash=excluded.cash,
                current_price=excluded.current_price,
                entry_price=excluded.entry_price,
                saved_at=excluded.saved_at,
                extra_json=excluded.extra_json
            """,
            (
                symbol,
                int(position.get("shares", 0) or 0),
                float(position.get("avg_cost", 0.0) or 0.0),
                float(position.get("total_invested", 0.0) or 0.0),
                float(position.get("cash", 0.0) or 0.0),
                float(position.get("current_price", position.get("avg_cost", 0.0)) or 0.0),
                float(position.get("entry_price", position.get("avg_cost", 0.0)) or 0.0),
                str(saved_at),
                json.dumps(extra_fields, ensure_ascii=False) if extra_fields else None,
            ),
        )
        conn.commit()

    return _resolve_db_path(positions_dir)


def load_position(symbol: str, positions_dir: Optional[str] = None) -> Optional[Dict]:
    symbol = _normalize_symbol(symbol)
    with _get_connection(positions_dir) as conn:
        row = conn.execute("SELECT * FROM positions WHERE symbol = ?", (symbol,)).fetchone()
    if not row:
        return None

    data = {
        "symbol": row["symbol"],
        "shares": int(row["shares"]),
        "avg_cost": float(row["avg_cost"]),
        "total_invested": float(row["total_invested"]),
        "cash": float(row["cash"]),
        "current_price": float(row["current_price"]),
        "entry_price": float(row["entry_price"]),
        "saved_at": row["saved_at"],
        "file_path": get_position_file_path(symbol, positions_dir=positions_dir),
    }

    if row["extra_json"]:
        try:
            def _resolve_db_path(db_path_env_var='POSITIONS_DB_PATH'):
                """Resolve database path, creating parent directory if needed.
    
                Supports:
                - Tilde expansion (~/.streamlit/positions.db)
                - Absolute paths (/full/path/to/positions.db)
                - Relative paths (./data/positions.db)
                """
                db_path = os.getenv(db_path_env_var, './data/positions.db')
    
                # Expand tilde to home directory
                db_path = os.path.expanduser(db_path)
    
                # Convert to absolute path
                abs_path = os.path.abspath(db_path)
                parent_dir = os.path.dirname(abs_path)
    
                if not os.path.exists(parent_dir):
                    try:
                        os.makedirs(parent_dir, exist_ok=True)
                        print(f"[POSITION_STORE] Created directory: {parent_dir}")
                    except PermissionError as e:
                        print(f"[POSITION_STORE] ⚠️ Permission denied creating {parent_dir}: {e}")
                        print(f"[POSITION_STORE] Trying fallback path...")
                        # Fallback to ./data/ if primary path fails
                        fallback_path = os.path.expanduser('./data/positions.db')
                        fallback_abs = os.path.abspath(fallback_path)
                        fallback_parent = os.path.dirname(fallback_abs)
                        os.makedirs(fallback_parent, exist_ok=True)
                        abs_path = fallback_abs
                        parent_dir = fallback_parent
                        print(f"[POSITION_STORE] Using fallback: {abs_path}")
    
                exists = os.path.exists(abs_path)
                size_bytes = os.path.getsize(abs_path) if exists else 0
                print(f"[POSITION_STORE] ✅ DB: {abs_path} | Exists: {exists} | Size: {size_bytes} bytes")
                return abs_path
            data.update(json.loads(row["extra_json"]))
        except Exception:
            pass

    return data


def list_positions(positions_dir: Optional[str] = None) -> List[Dict]:
    positions: List[Dict] = []
    with _get_connection(positions_dir) as conn:
        rows = conn.execute(
            "SELECT * FROM positions WHERE shares > 0 ORDER BY symbol ASC"
        ).fetchall()

    for row in rows:
        record = {
            "symbol": row["symbol"],
            "shares": int(row["shares"]),
            "avg_cost": float(row["avg_cost"]),
            "total_invested": float(row["total_invested"]),
            "cash": float(row["cash"]),
            "current_price": float(row["current_price"]),
            "entry_price": float(row["entry_price"]),
            "saved_at": row["saved_at"],
            "file_path": get_position_file_path(row["symbol"], positions_dir=positions_dir),
        }
        if row["extra_json"]:
            try:
                record.update(json.loads(row["extra_json"]))
            except Exception:
                pass
        positions.append(record)

    return positions


def _legacy_position_files(source_dirs: List[str]) -> List[str]:
    files: List[str] = []
    for source_dir in source_dirs:
        if not source_dir:
            continue
        pattern = os.path.join(source_dir, "*_position.json")
        files.extend(glob.glob(pattern))
    return files


def _load_legacy_json(path: str) -> Optional[Dict]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception:
        return None
    if not isinstance(data, dict) or not data.get("symbol"):
        return None
    return data


def migrate_positions(source_dirs: Optional[List[str]] = None, target_dir: Optional[str] = None) -> List[str]:
    """Migrate legacy JSON position files into SQLite.

    Args:
        source_dirs: Directories that may contain ``*_position.json`` files.
        target_dir: SQLite target (db file path or directory).

    Returns:
        List of migrated symbols.
    """
    candidates = source_dirs or ["logs", "data/positions"]
    migrated_symbols: List[str] = []

    for json_file in _legacy_position_files(candidates):
        legacy = _load_legacy_json(json_file)
        try:
            if not legacy:
                continue
            shares = int(legacy.get("shares", 0) or 0)
            if shares <= 0:
                continue
            symbol = _normalize_symbol(str(legacy.get("symbol", "")))
            save_position(legacy, positions_dir=target_dir)
            migrated_symbols.append(symbol)
        except Exception:
            continue

    return sorted(set(migrated_symbols))


def delete_position(symbol: str, positions_dir: Optional[str] = None) -> bool:
    symbol = _normalize_symbol(symbol)
    with _get_connection(positions_dir) as conn:
        cursor = conn.execute("DELETE FROM positions WHERE symbol = ?", (symbol,))
        conn.commit()
        return cursor.rowcount > 0

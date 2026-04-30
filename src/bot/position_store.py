"""Database-backed position storage helpers for Streamlit and paper trading."""
from __future__ import annotations

import glob
import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

try:
    import psycopg2
except ImportError:  # pragma: no cover - optional dependency for Postgres support
    psycopg2 = None

DEFAULT_POSITIONS_DB_URL = os.getenv("POSITIONS_DB_URL") or os.getenv("DATABASE_URL")
DEFAULT_POSITIONS_DB_PATH = os.getenv("POSITIONS_DB_PATH", "data/nepse_positions.db")
DEFAULT_LEGACY_POSITIONS_DIR = os.getenv("POSITIONS_DIR", "data/positions")


def _normalize_symbol(symbol: str) -> str:
    if not symbol:
        raise ValueError("Symbol is required")
    return symbol.strip().upper()


def _resolve_storage_target(storage_target: Optional[str] = None) -> str:
    """Return the active storage target (Postgres URL or SQLite path)."""
    if storage_target:
        return storage_target
    return DEFAULT_POSITIONS_DB_URL or DEFAULT_POSITIONS_DB_PATH


def _is_postgres_target(storage_target: str) -> bool:
    return storage_target.startswith("postgresql://") or storage_target.startswith("postgres://")


def _ensure_parent_dir(path: str) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def _connect(storage_target: Optional[str] = None):
    """Open a database connection and create the positions table if needed."""
    resolved_target = _resolve_storage_target(storage_target)

    if _is_postgres_target(resolved_target):
        if psycopg2 is None:
            raise RuntimeError("psycopg2-binary is required for Postgres storage")

        conn = psycopg2.connect(resolved_target)
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS positions (
                    symbol TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    shares INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL
                )
                """
            )
        conn.commit()
        return conn

    _ensure_parent_dir(resolved_target)
    conn = sqlite3.connect(resolved_target)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS positions (
            symbol TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            shares INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL
        )
        """
    )
    return conn


def get_position_file_path(symbol: str, positions_dir: Optional[str] = None) -> str:
    """Return a stable reference for the stored position.

    Kept for backwards compatibility with existing tests/UI code.
    """
    symbol = _normalize_symbol(symbol)
    storage_target = _resolve_storage_target(positions_dir)
    if _is_postgres_target(storage_target):
        return f"{storage_target}#{symbol.lower()}"
    return f"sqlite:///{storage_target}#{symbol.lower()}"


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
    """Build a position dictionary in the same format as the saved position payload."""
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


def save_position(position: Dict, positions_dir: Optional[str] = None) -> str:
    """Save a position dictionary to the configured database and return its target."""
    symbol = _normalize_symbol(position.get("symbol"))

    position_to_save = dict(position)
    position_to_save["symbol"] = symbol
    position_to_save.setdefault("saved_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    payload = json.dumps(position_to_save, ensure_ascii=False)
    shares = int(position_to_save.get("shares", 0) or 0)
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    storage_target = _resolve_storage_target(positions_dir)

    if _is_postgres_target(storage_target):
        with _connect(storage_target) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO positions (symbol, payload, shares, updated_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT(symbol) DO UPDATE SET
                        payload = EXCLUDED.payload,
                        shares = EXCLUDED.shares,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (symbol, payload, shares, updated_at),
                )
            conn.commit()
        return storage_target

    with _connect(storage_target) as conn:
        conn.execute(
            """
            INSERT INTO positions (symbol, payload, shares, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
                payload = excluded.payload,
                shares = excluded.shares,
                updated_at = excluded.updated_at
            """,
            (symbol, payload, shares, updated_at),
        )
        conn.commit()

    return storage_target


def load_position(symbol: str, positions_dir: Optional[str] = None) -> Optional[Dict]:
    """Load a saved position for a symbol, if it exists."""
    symbol = _normalize_symbol(symbol)
    storage_target = _resolve_storage_target(positions_dir)

    try:
        with _connect(storage_target) as conn:
            if _is_postgres_target(storage_target):
                with conn.cursor() as cursor:
                    cursor.execute("SELECT payload FROM positions WHERE symbol = %s", (symbol,))
                    row = cursor.fetchone()
            else:
                row = conn.execute(
                    "SELECT payload FROM positions WHERE symbol = ?",
                    (symbol,),
                ).fetchone()
    except Exception:
        return None

    if not row:
        return None

    try:
        payload = row[0] if _is_postgres_target(storage_target) else row["payload"]
        data = json.loads(payload)
    except (TypeError, json.JSONDecodeError):
        return None

    if not data.get("symbol"):
        return None

    data["storage_path"] = storage_target
    data["file_path"] = get_position_file_path(symbol, positions_dir=storage_target)
    return data


def list_positions(positions_dir: Optional[str] = None) -> List[Dict]:
    """Return all saved positions from the configured database."""
    storage_target = _resolve_storage_target(positions_dir)
    positions: List[Dict] = []

    try:
        with _connect(storage_target) as conn:
            if _is_postgres_target(storage_target):
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT payload, shares FROM positions WHERE shares > 0 ORDER BY symbol"
                    )
                    rows = cursor.fetchall()
            else:
                rows = conn.execute(
                    "SELECT payload, shares FROM positions WHERE shares > 0 ORDER BY symbol"
                ).fetchall()
    except Exception:
        return positions

    for row in rows:
        try:
            payload = row[0] if _is_postgres_target(storage_target) else row["payload"]
            shares = row[1] if _is_postgres_target(storage_target) else row["shares"]
            data = json.loads(payload)
            if data.get("symbol") and int(shares) > 0:
                data["storage_path"] = storage_target
                data["file_path"] = get_position_file_path(str(data["symbol"]), positions_dir=storage_target)
                positions.append(data)
        except (TypeError, json.JSONDecodeError, ValueError):
            continue

    return positions


def delete_position(symbol: str, positions_dir: Optional[str] = None) -> bool:
    """Delete a saved position from the configured database and clean up legacy files."""
    symbol = _normalize_symbol(symbol)
    storage_target = _resolve_storage_target(positions_dir)
    removed_any = False

    try:
        with _connect(storage_target) as conn:
            if _is_postgres_target(storage_target):
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM positions WHERE symbol = %s", (symbol,))
                    removed_any = cursor.rowcount > 0
                conn.commit()
            else:
                cursor = conn.execute("DELETE FROM positions WHERE symbol = ?", (symbol,))
                conn.commit()
                removed_any = cursor.rowcount > 0
    except Exception:
        pass

    # Remove associated bot log file
    log_path = os.path.join("logs", f"{symbol.lower()}_bot.log")
    if os.path.exists(log_path):
        try:
            os.remove(log_path)
            removed_any = True
        except OSError:
            pass

    # Remove legacy JSON copies so they cannot be re-imported later
    legacy_dirs = {"logs", DEFAULT_LEGACY_POSITIONS_DIR, os.getenv("POSITIONS_DIR", DEFAULT_LEGACY_POSITIONS_DIR)}
    for directory in legacy_dirs:
        legacy_path = os.path.join(directory, f"{symbol.lower()}_position.json")
        if os.path.exists(legacy_path):
            try:
                os.remove(legacy_path)
                removed_any = True
            except OSError:
                pass

    return removed_any


def migrate_positions(source_dirs: Optional[List[str]] = None, target_dir: Optional[str] = None) -> List[str]:
    """Import legacy JSON files into SQLite.

    By default, this migrates from `logs/` and from the older JSON storage
    directory used before SQLite was introduced.
    """
    storage_target = _resolve_storage_target(target_dir)
    if not _is_postgres_target(storage_target):
        _ensure_parent_dir(storage_target)

    try:
        with _connect(storage_target) as conn:
            if _is_postgres_target(storage_target):
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(1) FROM positions")
                    existing_count = cursor.fetchone()[0]
            else:
                existing_count = conn.execute("SELECT COUNT(1) AS count FROM positions").fetchone()["count"]
    except Exception:
        existing_count = 0

    if existing_count:
        return []

    if source_dirs is None:
        source_dirs = ["logs", DEFAULT_LEGACY_POSITIONS_DIR]

    copied_sources: List[str] = []
    seen_paths = set()

    for source_dir in source_dirs:
        pattern = os.path.join(source_dir, "*_position.json")
        for source_path in glob.glob(pattern):
            if source_path in seen_paths:
                continue
            seen_paths.add(source_path)
            try:
                with open(source_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                if not data.get("symbol"):
                    continue
                save_position(data, positions_dir=storage_target)
                copied_sources.append(source_path)
            except (OSError, json.JSONDecodeError, ValueError, TypeError):
                continue

    return copied_sources

"""Simple file-based position storage using JSON files.

This module stores positions as JSON files in a directory (default `logs/`).
Functions accept an optional `positions_dir` parameter for compatibility with
existing call sites.
"""
from __future__ import annotations

import glob
import json
import os
from datetime import datetime
from typing import Dict, List, Optional


DEFAULT_POSITIONS_DIR = os.getenv("POSITIONS_DIR", "logs")


def _normalize_symbol(symbol: str) -> str:
    if not symbol:
        raise ValueError("Symbol is required")
    return symbol.strip().upper()


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def get_position_file_path(symbol: str, positions_dir: Optional[str] = None) -> str:
    symbol = _normalize_symbol(symbol)
    dirpath = positions_dir or DEFAULT_POSITIONS_DIR
    _ensure_dir(dirpath)
    return os.path.join(dirpath, f"{symbol.lower()}_position.json")


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
    position_to_save = dict(position)
    position_to_save["symbol"] = symbol
    position_to_save.setdefault("saved_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    dirpath = positions_dir or DEFAULT_POSITIONS_DIR
    _ensure_dir(dirpath)
    path = get_position_file_path(symbol, positions_dir=dirpath)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(position_to_save, f, ensure_ascii=False, indent=2)
    return path


def load_position(symbol: str, positions_dir: Optional[str] = None) -> Optional[Dict]:
    symbol = _normalize_symbol(symbol)
    path = get_position_file_path(symbol, positions_dir=positions_dir)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None
    if not data.get("symbol"):
        return None
    data["file_path"] = path
    return data


def list_positions(positions_dir: Optional[str] = None) -> List[Dict]:
    dirpath = positions_dir or DEFAULT_POSITIONS_DIR
    _ensure_dir(dirpath)
    positions: List[Dict] = []
    pattern = os.path.join(dirpath, "*_position.json")
    for path in glob.glob(pattern):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            shares = int(data.get("shares", 0) or 0)
            if data.get("symbol") and shares > 0:
                data["file_path"] = path
                positions.append(data)
        except Exception:
            continue
    return positions


def delete_position(symbol: str, positions_dir: Optional[str] = None) -> bool:
    symbol = _normalize_symbol(symbol)
    path = get_position_file_path(symbol, positions_dir=positions_dir)
    removed = False
    if os.path.exists(path):
        try:
            os.remove(path)
            removed = True
        except OSError:
            removed = False
    # remove bot log as well
    log_path = os.path.join("logs", f"{symbol.lower()}_bot.log")
    if os.path.exists(log_path):
        try:
            os.remove(log_path)
            removed = True
        except OSError:
            pass
    return removed


def migrate_positions(source_dirs: Optional[List[str]] = None, target_dir: Optional[str] = None) -> List[str]:
    # No-op for now; keep for compat but do not move files between stores
    return []

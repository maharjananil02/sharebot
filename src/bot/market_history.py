"""
Weekly market history storage and selection helpers.

Stores one snapshot per day (or per run) and uses up to 7 days of history
for better share selection.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional

from .logger import setup_logger

logger = setup_logger(__name__)


def _to_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _json_safe(value):
    """Convert common non-JSON types to JSON-safe values."""
    if isinstance(value, (datetime, date)):
        return value.isoformat(sep=" ") if isinstance(value, datetime) else value.isoformat()
    if isinstance(value, dict):
        return {key: _json_safe(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    return value


class WeeklyMarketHistory:
    """Persist and analyze up to one week of market snapshots."""

    def __init__(self, history_file: str = "logs/market_history.json", max_days: int = 7):
        self.history_file = history_file
        self.max_days = int(max_days)
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)

    def load_history(self) -> List[Dict]:
        """Load saved snapshots from disk."""
        if not os.path.exists(self.history_file):
            return []

        try:
            with open(self.history_file, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return []

        if isinstance(data, dict):
            data = data.get("snapshots", [])
        if not isinstance(data, list):
            return []
        return data

    def save_history(self, snapshots: List[Dict]) -> None:
        """Save snapshots to disk."""
        with open(self.history_file, "w", encoding="utf-8") as file:
            json.dump({"snapshots": _json_safe(snapshots)}, file, indent=2)

    def _prune_to_recent_days(self, snapshots: List[Dict]) -> List[Dict]:
        """Keep only the most recent unique days up to max_days."""
        if not snapshots:
            return []

        by_day: Dict[str, Dict] = {}
        for snapshot in snapshots:
            day = snapshot.get("date") or snapshot.get("captured_at", "")[:10]
            if day:
                by_day[day] = snapshot

        recent_days = sorted(by_day.keys())[-self.max_days :]
        return [by_day[day] for day in recent_days]

    def add_snapshot(self, stocks: Dict[str, Dict], captured_at: Optional[str] = None) -> List[Dict]:
        """Add a market snapshot and prune to the most recent days."""
        captured_at = captured_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        safe_stocks = _json_safe(stocks)
        snapshot = {
            "date": captured_at[:10],
            "captured_at": captured_at,
            "stocks": safe_stocks,
        }

        snapshots = self.load_history()
        snapshots.append(snapshot)
        snapshots = self._prune_to_recent_days(snapshots)
        self.save_history(snapshots)
        return snapshots

    def get_snapshot_count(self) -> int:
        """Return the number of saved day snapshots."""
        return len(self.load_history())

    def get_weekly_top_stocks(
        self,
        current_snapshot: Dict[str, Dict],
        top_n: int = 5,
        min_volume: int = 50000,
        min_momentum: float = 0.0,
    ) -> List[Tuple[str, Dict, float]]:
        """
        Score stocks using one week of history plus the current snapshot.

        Score is based on:
        - average weekly volume
        - average weekly momentum
        - consistency of positive days
        - latest snapshot as the purchase price source
        """
        snapshots = self.load_history()

        # Ensure the current snapshot is always included in the analysis.
        current_day = datetime.now().strftime("%Y-%m-%d")
        if not snapshots or snapshots[-1].get("date") != current_day:
            snapshots = snapshots + [
                {
                    "date": current_day,
                    "captured_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "stocks": _json_safe(current_snapshot),
                }
            ]
        else:
            # Replace the latest day with the fresh snapshot.
            snapshots = snapshots[:-1] + [
                {
                    "date": current_day,
                    "captured_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "stocks": _json_safe(current_snapshot),
                }
            ]

        snapshots = self._prune_to_recent_days(snapshots)

        by_symbol: Dict[str, List[Dict]] = defaultdict(list)
        for snapshot in snapshots:
            snap_date = snapshot.get("date") or snapshot.get("captured_at", "")[:10]
            for symbol, data in (snapshot.get("stocks") or {}).items():
                by_symbol[str(symbol).upper()].append(
                    {
                        "date": snap_date,
                        "ltp": _to_float(data.get("ltp")),
                        "volume": _to_int(data.get("volume")),
                        "pct_change": _to_float(data.get("pct_change")),
                        "change": _to_float(data.get("change")),
                        "open": _to_float(data.get("open")),
                        "high": _to_float(data.get("high")),
                        "low": _to_float(data.get("low")),
                    }
                )

        if not by_symbol:
            return []

        strict_aggregates: List[Tuple[str, Dict, float]] = []
        fallback_aggregates: List[Tuple[str, Dict, float]] = []

        for symbol, records in by_symbol.items():
            records = sorted(records, key=lambda item: item["date"])
            latest = records[-1]
            avg_volume = sum(r["volume"] for r in records) / len(records)
            avg_change = sum(r["pct_change"] for r in records) / len(records)
            positive_days = sum(1 for r in records if r["pct_change"] >= 0)
            consistency = positive_days / len(records)
            trend_delta = latest["pct_change"] - records[0]["pct_change"]

            aggregate_data = {
                "symbol": symbol,
                "ltp": latest["ltp"],
                "volume": int(avg_volume),
                "pct_change": latest["pct_change"],
                "avg_volume": int(avg_volume),
                "avg_pct_change": round(avg_change, 2),
                "positive_days": positive_days,
                "days_observed": len(records),
                "consistency": round(consistency, 2),
                "trend_delta": round(trend_delta, 2),
                "history_start": records[0]["date"],
                "history_end": records[-1]["date"],
                "latest_change": latest["pct_change"],
                "latest_volume": latest["volume"],
            }

            passes_volume = avg_volume >= min_volume
            passes_momentum = not (
                latest["pct_change"] < min_momentum and avg_change < min_momentum
            )

            # Primary candidates that satisfy configured quality filters.
            if passes_volume and passes_momentum:
                strict_aggregates.append((symbol, aggregate_data, 0.0))
            else:
                # Fallback pool used only when strict candidates are fewer than requested.
                fallback_aggregates.append((symbol, aggregate_data, 0.0))

        aggregates = list(strict_aggregates)

        if len(aggregates) < top_n and fallback_aggregates:
            selected_symbols = {symbol for symbol, _, _ in aggregates}
            fallback_aggregates.sort(
                key=lambda item: (item[1]["avg_volume"], item[1]["avg_pct_change"]),
                reverse=True,
            )

            for symbol, aggregate_data, score in fallback_aggregates:
                if symbol in selected_symbols:
                    continue
                aggregates.append((symbol, aggregate_data, score))
                selected_symbols.add(symbol)
                if len(aggregates) >= top_n:
                    break

        if not aggregates:
            return []

        max_volume = max(item[1]["avg_volume"] for item in aggregates) or 1
        max_change = max(item[1]["avg_pct_change"] for item in aggregates)
        min_change = min(item[1]["avg_pct_change"] for item in aggregates)
        change_span = max(max_change - min_change, 1e-9)

        scored: List[Tuple[str, Dict, float]] = []
        for symbol, aggregate_data, _ in aggregates:
            volume_score = aggregate_data["avg_volume"] / max_volume
            momentum_score = (aggregate_data["avg_pct_change"] - min_change) / change_span
            consistency_score = aggregate_data["consistency"]
            trend_score = 1.0 if aggregate_data["trend_delta"] > 0 else 0.0

            score = (
                volume_score * 0.40
                + momentum_score * 0.30
                + consistency_score * 0.20
                + trend_score * 0.10
            )
            scored.append((symbol, aggregate_data, round(score, 3)))

        scored.sort(key=lambda item: item[2], reverse=True)
        return scored[:top_n]

import tempfile
import unittest

from src.bot.trade_history import (
    clear_trade_history,
    get_trade_history,
    get_trade_statistics,
    get_trades_by_symbol,
    record_trade,
)


class TradeHistoryTests(unittest.TestCase):
    def test_record_and_statistics(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            clear_trade_history(logs_dir=tmpdir)

            first = record_trade(
                symbol="AHL",
                quantity=10,
                buy_price=100,
                sell_price=120,
                pnl=200,
                pnl_pct=20,
                sell_timestamp="2026-04-29 10:00:00",
                logs_dir=tmpdir,
            )
            second = record_trade(
                symbol="AHL",
                quantity=5,
                buy_price=100,
                sell_price=90,
                pnl=-50,
                pnl_pct=-10,
                sell_timestamp="2026-04-29 11:00:00",
                logs_dir=tmpdir,
            )

            self.assertEqual(first["symbol"], "AHL")
            self.assertEqual(second["quantity"], 5)

            history = get_trade_history(logs_dir=tmpdir)
            self.assertEqual(len(history), 2)
            self.assertEqual(history[0]["sold_at"], "2026-04-29 11:00:00")

            by_symbol = get_trades_by_symbol("ahl", logs_dir=tmpdir)
            self.assertEqual(len(by_symbol), 2)

            stats = get_trade_statistics(logs_dir=tmpdir)
            self.assertEqual(stats["total_trades"], 2)
            self.assertEqual(stats["profitable_trades"], 1)
            self.assertEqual(stats["losing_trades"], 1)
            self.assertEqual(stats["total_quantity_sold"], 15)
            self.assertEqual(stats["total_pnl"], 150.0)

    def test_clear_trade_history(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            record_trade(
                symbol="BARUN",
                quantity=1,
                buy_price=50,
                sell_price=55,
                pnl=5,
                pnl_pct=10,
                logs_dir=tmpdir,
            )
            self.assertTrue(clear_trade_history(logs_dir=tmpdir))
            self.assertEqual(get_trade_history(logs_dir=tmpdir), [])


if __name__ == "__main__":
    unittest.main()
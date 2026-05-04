import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.bot.stock_trader import StockPaperTrader
from src.bot.position_store import load_position


class FakeStrategy:
    def __init__(self, entry_price=100.0, stop_loss=90.0, total_quantity=10):
        self.entry_price = entry_price
        self.current_stop_loss = stop_loss
        self.stop_loss_pct = 10
        self.total_quantity = total_quantity
        self.analyze_calls = []

    def analyze(self, current_price):
        self.analyze_calls.append(current_price)
        return []

    def _get_average_entry_price(self):
        return self.entry_price

    def _calculate_position_pct_change(self):
        return ((self.analyze_calls[-1] - self.entry_price) / self.entry_price) * 100

    def get_order_summary(self, pending_orders):
        return "SUMMARY"

    def execute_order(self, order, price):
        return None


class StockTraderTests(unittest.TestCase):
    def test_save_position_state_includes_stop_loss(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/positions.db"
            trader = StockPaperTrader(symbol="AHL", check_interval=30, positions_db_path=db_path)
            trader.position_state_file = db_path
            trader.paper_trader.seed_position("AHL", 10, 100)
            trader.current_price = 120
            trader.strategy = FakeStrategy(entry_price=100, stop_loss=90, total_quantity=10)

            trader.save_position_state()

            content = load_position("AHL", positions_dir=db_path)
            self.assertIsNotNone(content)

            self.assertEqual(content["stop_loss"], 90)

    def test_deactivate_closed_position_clears_state(self):
        trader = StockPaperTrader(symbol="AHL", check_interval=30, log_file="logs/test_ahl.log")
        trader.strategy = FakeStrategy()
        trader.current_price = 100
        trader.price_history = [100]
        trader.last_stop_loss = 90
        trader.stoploss_alerted = True

        trader._deactivate_closed_position()

        self.assertIsNone(trader.strategy)
        self.assertIsNone(trader.current_price)
        self.assertEqual(trader.price_history, [])
        self.assertIsNone(trader.last_stop_loss)
        self.assertFalse(trader.stoploss_alerted)

    @patch.object(StockPaperTrader, "_has_open_position", return_value=False)
    @patch.object(StockPaperTrader, "save_position_state")
    def test_check_price_stops_when_position_closed(self, mock_save_state, mock_has_open):
        trader = StockPaperTrader(symbol="AHL", check_interval=30, log_file="logs/test_ahl.log")
        trader.strategy = FakeStrategy()
        trader._deactivate_closed_position = MagicMock()

        trader.check_price_and_execute()

        mock_save_state.assert_called_once()
        trader._deactivate_closed_position.assert_called_once()

    @patch("src.bot.stock_trader.send_email_notification", return_value=True)
    @patch.object(StockPaperTrader, "save_position_state")
    def test_stop_loss_update_sends_email(self, mock_save_state, mock_send_email):
        trader = StockPaperTrader(symbol="AHL", check_interval=30, log_file="logs/test_ahl.log")
        trader.strategy = FakeStrategy(entry_price=100, stop_loss=90, total_quantity=10)
        trader.last_stop_loss = 85
        trader.current_price = 120
        trader.price_history = [100]
        trader.simulate_price_movement = MagicMock(return_value=120)

        trader.paper_trader.seed_position("AHL", 10, 100)
        trader.check_price_and_execute()

        mock_send_email.assert_called()
        mock_save_state.assert_called()


if __name__ == "__main__":
    unittest.main()
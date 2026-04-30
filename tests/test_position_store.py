import tempfile
import unittest
from pathlib import Path

from src.bot.position_store import (
    build_position_record,
    delete_position,
    get_position_file_path,
    list_positions,
    load_position,
    save_position,
)


class PositionStoreTests(unittest.TestCase):
    def test_build_position_record_defaults(self):
        record = build_position_record(symbol="gufl", shares=10, avg_cost=100)
        self.assertEqual(record["symbol"], "GUFL")
        self.assertEqual(record["shares"], 10)
        self.assertEqual(record["avg_cost"], 100.0)
        self.assertEqual(record["total_invested"], 1000.0)
        self.assertEqual(record["current_price"], 100.0)
        self.assertEqual(record["entry_price"], 100.0)

    def test_save_load_list_delete_position(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            position = build_position_record(
                symbol="BBC",
                shares=200,
                avg_cost=80,
                current_price=120,
                entry_price=80,
            )
            db_path = str(Path(tmpdir) / "positions.db")
            saved_path = save_position(position, positions_dir=db_path)
            self.assertEqual(saved_path, db_path)
            self.assertTrue(Path(saved_path).exists())

            loaded = load_position("bbc", positions_dir=db_path)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded["symbol"], "BBC")
            self.assertEqual(loaded["shares"], 200)

            listed = list_positions(positions_dir=db_path)
            self.assertEqual(len(listed), 1)
            self.assertEqual(listed[0]["symbol"], "BBC")
            self.assertIn("file_path", listed[0])

            file_path = get_position_file_path("BBC", positions_dir=db_path)
            self.assertTrue(file_path.startswith("sqlite:///"))

            self.assertTrue(delete_position("BBC", positions_dir=db_path))
            self.assertEqual(list_positions(positions_dir=db_path), [])
            self.assertIsNone(load_position("BBC", positions_dir=db_path))


if __name__ == "__main__":
    unittest.main()
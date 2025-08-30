"""
Tests for example scripts to ensure they don't become stale.

These tests verify that the example scripts can be imported and run
without errors (though they may skip execution if API keys are missing).
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the manifoldbot package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestExamples(unittest.TestCase):
    """Test that example scripts are importable and runnable."""

    def test_basic_reader_example_imports(self):
        """Test that basic_reader.py can be imported."""
        try:
            from manifoldbot.examples.basic_reader import main

            self.assertTrue(callable(main))
        except ImportError as e:
            self.fail(f"Could not import basic_reader example: {e}")

    def test_basic_writer_example_imports(self):
        """Test that basic_writer.py can be imported."""
        try:
            from manifoldbot.examples.basic_writer import main

            self.assertTrue(callable(main))
        except ImportError as e:
            self.fail(f"Could not import basic_writer example: {e}")

    def test_simple_trading_bot_example_imports(self):
        """Test that simple_trading_bot.py can be imported."""
        try:
            from manifoldbot.examples.simple_trading_bot import (
                SimpleTradingBot, main)

            self.assertTrue(callable(SimpleTradingBot))
            self.assertTrue(callable(main))
        except ImportError as e:
            self.fail(f"Could not import simple_trading_bot example: {e}")

    @patch("manifoldbot.examples.basic_reader.ManifoldReader")
    def test_basic_reader_example_runs(self, mock_reader_class):
        """Test that basic_reader example can run without errors."""
        # Mock the reader
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        # Mock market data
        mock_reader.get_markets.return_value = [
            {"question": "Test market 1", "probability": 0.5, "volume": 1000}
        ]
        mock_reader.get_market_by_slug.return_value = {
            "question": "Test market by slug",
            "probability": 0.6,
            "volume": 500,
        }
        mock_reader.search_markets.return_value = [
            {"question": "AI test market", "probability": 0.3, "volume": 200}
        ]

        # Import and run
        from manifoldbot.examples.basic_reader import main

        # Should not raise any exceptions
        try:
            main()
        except Exception as e:
            self.fail(f"basic_reader example failed to run: {e}")

    @patch("manifoldbot.examples.basic_writer.ManifoldWriter")
    def test_basic_writer_example_runs(self, mock_writer_class):
        """Test that basic_writer example can run without errors."""
        # Mock the writer
        mock_writer = MagicMock()
        mock_writer_class.return_value = mock_writer
        mock_writer.is_authenticated.return_value = True
        mock_writer.get_me.return_value = {"name": "Test User"}
        mock_writer.get_balance.return_value = 100.0
        mock_writer.get_total_deposits.return_value = 200.0
        mock_writer.get_portfolio.return_value = {"totalValue": 100}
        mock_writer.get_positions.return_value = []
        mock_writer.calculate_market_impact.return_value = {
            "current_probability": 0.5,
            "estimated_impact": 0.01,
            "new_probability": 0.51,
        }

        # Mock environment variable
        with patch.dict(os.environ, {"MANIFOLD_API_KEY": "test_key"}):
            from manifoldbot.examples.basic_writer import main

            # Should not raise any exceptions
            try:
                main()
            except Exception as e:
                self.fail(f"basic_writer example failed to run: {e}")

    def test_basic_writer_example_without_api_key(self):
        """Test that basic_writer handles missing API key gracefully."""
        # Remove API key from environment
        with patch.dict(os.environ, {}, clear=True):
            from manifoldbot.examples.basic_writer import main

            # Should not raise any exceptions
            try:
                main()
            except Exception as e:
                self.fail(f"basic_writer failed to handle missing key: {e}")

    @patch("manifoldbot.examples.simple_trading_bot.ManifoldReader")
    @patch("manifoldbot.examples.simple_trading_bot.ManifoldWriter")
    def test_simple_trading_bot_example_runs(
        self, mock_writer_class, mock_reader_class
    ):
        """Test that simple_trading_bot can run without errors."""
        # Mock the reader
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.get_markets.return_value = [
            {
                "id": "test_market_1",
                "question": "AI will dominate by 2030",
                "probability": 0.2,
                "volume": 500,
                "isResolved": False,
            }
        ]

        # Mock the writer
        mock_writer = MagicMock()
        mock_writer_class.return_value = mock_writer
        mock_writer.is_authenticated.return_value = True
        mock_writer.get_balance.return_value = 50.0
        mock_writer.place_bet.return_value = {"betId": "test_bet_123"}

        # Mock environment variable
        with patch.dict(os.environ, {"MANIFOLD_API_KEY": "test_key"}):
            from manifoldbot.examples.simple_trading_bot import main

            # Should not raise any exceptions
            try:
                main()
            except Exception as e:
                self.fail(f"simple_trading_bot example failed to run: {e}")


if __name__ == "__main__":
    unittest.main()

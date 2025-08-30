"""
Tests for the generic ManifoldBot framework.
"""

import pytest
from unittest.mock import patch, MagicMock

from manifoldbot.manifold.bot import (
    ManifoldBot, DecisionMaker, MarketDecision, TradingSession,
    CallbackDecisionMaker, RandomDecisionMaker
)


class MockDecisionMaker(DecisionMaker):
    """Test decision maker for unit tests."""
    
    def __init__(self, decision: str = "SKIP", confidence: float = 0.5, reasoning: str = "Test"):
        self.decision = decision
        self.confidence = confidence
        self.reasoning = reasoning
    
    def analyze_market(self, market):
        return MarketDecision(
            market_id=market.get("id", "test"),
            question=market.get("question", "Test question"),
            current_probability=market.get("probability", 0.5),
            decision=self.decision,
            confidence=self.confidence,
            reasoning=self.reasoning
        )


class TestManifoldBot:
    """Test cases for ManifoldBot."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_decision_maker = MockDecisionMaker()
    
    @patch('manifoldbot.manifold.bot.ManifoldWriter')
    @patch('manifoldbot.manifold.bot.ManifoldReader')
    def test_bot_init(self, mock_reader_class, mock_writer_class):
        """Test bot initialization."""
        # Mock the writer
        mock_writer = MagicMock()
        mock_writer.is_authenticated.return_value = True
        mock_writer.get_balance.return_value = 100.0
        mock_writer_class.return_value = mock_writer
        
        # Mock the reader
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        
        # Create bot
        bot = ManifoldBot(
            manifold_api_key="test_key",
            decision_maker=self.test_decision_maker
        )
        
        assert bot.writer == mock_writer
        assert bot.reader == mock_reader
        assert bot.decision_maker == self.test_decision_maker
    
    @patch('manifoldbot.manifold.bot.ManifoldWriter')
    @patch('manifoldbot.manifold.bot.ManifoldReader')
    def test_bot_init_with_callback(self, mock_reader_class, mock_writer_class):
        """Test bot initialization with callback function."""
        # Mock the writer
        mock_writer = MagicMock()
        mock_writer.is_authenticated.return_value = True
        mock_writer.get_balance.return_value = 100.0
        mock_writer_class.return_value = mock_writer
        
        # Mock the reader
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        
        # Create callback function
        def callback(market):
            return MarketDecision(
                market_id=market.get("id", "test"),
                question=market.get("question", "Test"),
                current_probability=market.get("probability", 0.5),
                decision="YES",
                confidence=0.8,
                reasoning="Callback decision"
            )
        
        # Create bot with callback
        bot = ManifoldBot(
            manifold_api_key="test_key",
            decision_maker=callback
        )
        
        assert isinstance(bot.decision_maker, CallbackDecisionMaker)
        assert bot.decision_maker.callback == callback
    
    @patch('manifoldbot.manifold.bot.ManifoldWriter')
    @patch('manifoldbot.manifold.bot.ManifoldReader')
    def test_analyze_market(self, mock_reader_class, mock_writer_class):
        """Test market analysis."""
        # Mock the writer
        mock_writer = MagicMock()
        mock_writer.is_authenticated.return_value = True
        mock_writer.get_balance.return_value = 100.0
        mock_writer_class.return_value = mock_writer
        
        # Mock the reader
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        
        # Create bot
        bot = ManifoldBot(
            manifold_api_key="test_key",
            decision_maker=self.test_decision_maker
        )
        
        # Test market analysis
        market = {
            "id": "test123",
            "question": "Will it rain?",
            "probability": 0.6
        }
        
        decision = bot.analyze_market(market)
        
        assert decision.market_id == "test123"
        assert decision.question == "Will it rain?"
        assert decision.current_probability == 0.6
        assert decision.decision == "SKIP"
        assert decision.confidence == 0.5
        assert decision.reasoning == "Test"
    
    @patch('manifoldbot.manifold.bot.ManifoldWriter')
    @patch('manifoldbot.manifold.bot.ManifoldReader')
    def test_place_bet_if_decision(self, mock_reader_class, mock_writer_class):
        """Test bet placement."""
        # Mock the writer
        mock_writer = MagicMock()
        mock_writer.is_authenticated.return_value = True
        mock_writer.get_balance.return_value = 100.0
        mock_writer.place_bet.return_value = {"id": "bet123"}
        mock_writer_class.return_value = mock_writer
        
        # Mock the reader
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        
        # Create bot
        bot = ManifoldBot(
            manifold_api_key="test_key",
            decision_maker=self.test_decision_maker
        )
        
        # Test SKIP decision
        skip_decision = MarketDecision(
            market_id="test123",
            question="Test question",
            current_probability=0.5,
            decision="SKIP",
            confidence=0.5,
            reasoning="Test"
        )
        
        result = bot.place_bet_if_decision(skip_decision, default_bet_amount=10)
        assert result is False
        mock_writer.place_bet.assert_not_called()
        
        # Test YES decision
        yes_decision = MarketDecision(
            market_id="test123",
            question="Test question",
            current_probability=0.5,
            decision="YES",
            confidence=0.8,
            reasoning="Test"
        )
        
        result = bot.place_bet_if_decision(yes_decision, default_bet_amount=10)
        assert result is True
        mock_writer.place_bet.assert_called_once_with(
            market_id="test123",
            outcome="YES",
            amount=10
        )
    
    @patch('manifoldbot.manifold.bot.ManifoldWriter')
    @patch('manifoldbot.manifold.bot.ManifoldReader')
    def test_run_on_markets(self, mock_reader_class, mock_writer_class):
        """Test running bot on a list of markets."""
        # Mock the writer
        mock_writer = MagicMock()
        mock_writer.is_authenticated.return_value = True
        mock_writer.get_balance.return_value = 100.0
        mock_writer.place_bet.return_value = {"id": "bet123"}
        mock_writer_class.return_value = mock_writer
        
        # Mock the reader
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        
        # Create bot with YES decision maker
        yes_decision_maker = MockDecisionMaker(decision="YES", confidence=0.8)
        bot = ManifoldBot(
            manifold_api_key="test_key",
            decision_maker=yes_decision_maker
        )
        
        # Test markets
        markets = [
            {"id": "market1", "question": "Question 1", "probability": 0.5},
            {"id": "market2", "question": "Question 2", "probability": 0.6}
        ]
        
        session = bot.run_on_markets(markets, bet_amount=5, max_bets=2)
        
        assert session.markets_analyzed == 2
        assert session.bets_placed == 2  # Two bets for two markets
        assert session.initial_balance == 100.0
        assert len(session.decisions) == 2
        assert len(session.errors) == 0
    
    @patch('manifoldbot.manifold.bot.ManifoldWriter')
    @patch('manifoldbot.manifold.bot.ManifoldReader')
    def test_run_on_recent_markets(self, mock_reader_class, mock_writer_class):
        """Test running bot on recent markets."""
        # Mock the writer
        mock_writer = MagicMock()
        mock_writer.is_authenticated.return_value = True
        mock_writer.get_balance.return_value = 100.0
        mock_writer_class.return_value = mock_writer
        
        # Mock the reader
        mock_reader = MagicMock()
        mock_reader.get_markets.return_value = [
            {"id": "market1", "question": "Question 1", "probability": 0.5}
        ]
        mock_reader_class.return_value = mock_reader
        
        # Create bot
        bot = ManifoldBot(
            manifold_api_key="test_key",
            decision_maker=self.test_decision_maker
        )
        
        session = bot.run_on_recent_markets(limit=5, bet_amount=10, max_bets=1)
        
        assert session.markets_analyzed == 1
        mock_reader.get_markets.assert_called_once_with(limit=5)
    
    @patch('manifoldbot.manifold.bot.ManifoldWriter')
    @patch('manifoldbot.manifold.bot.ManifoldReader')
    def test_run_on_user_markets(self, mock_reader_class, mock_writer_class):
        """Test running bot on user markets."""
        # Mock the writer
        mock_writer = MagicMock()
        mock_writer.is_authenticated.return_value = True
        mock_writer.get_balance.return_value = 100.0
        mock_writer_class.return_value = mock_writer
        
        # Mock the reader
        mock_reader = MagicMock()
        mock_reader.get_user.return_value = {"id": "user123", "name": "TestUser"}
        mock_reader.get_user_markets.return_value = [
            {"id": "market1", "question": "Question 1", "probability": 0.5}
        ]
        mock_reader_class.return_value = mock_reader
        
        # Create bot
        bot = ManifoldBot(
            manifold_api_key="test_key",
            decision_maker=self.test_decision_maker
        )
        
        session = bot.run_on_user_markets(username="TestUser", limit=5, bet_amount=10, max_bets=1)
        
        assert session.markets_analyzed == 1
        mock_reader.get_user.assert_called_once_with("TestUser")
        mock_reader.get_user_markets.assert_called_once_with("user123", limit=5)


class TestRandomDecisionMaker:
    """Test cases for RandomDecisionMaker."""
    
    def test_analyze_market_low_probability(self):
        """Test decision making for low probability markets."""
        decision_maker = RandomDecisionMaker()
        
        market = {
            "id": "test123",
            "question": "Will it rain?",
            "probability": 0.2
        }
        
        decision = decision_maker.analyze_market(market)
        
        assert decision.decision == "YES"
        assert decision.confidence == 0.8
        assert "too low" in decision.reasoning
    
    def test_analyze_market_high_probability(self):
        """Test decision making for high probability markets."""
        decision_maker = RandomDecisionMaker()
        
        market = {
            "id": "test123",
            "question": "Will it rain?",
            "probability": 0.8
        }
        
        decision = decision_maker.analyze_market(market)
        
        assert decision.decision == "NO"
        assert decision.confidence == 0.8
        assert "too high" in decision.reasoning
    
    def test_analyze_market_middle_probability(self):
        """Test decision making for middle probability markets."""
        decision_maker = RandomDecisionMaker()
        
        market = {
            "id": "test123",
            "question": "Will it rain?",
            "probability": 0.5
        }
        
        decision = decision_maker.analyze_market(market)
        
        assert decision.decision == "SKIP"
        assert decision.confidence == 0.5
        assert "reasonable range" in decision.reasoning


class TestCallbackDecisionMaker:
    """Test cases for CallbackDecisionMaker."""
    
    def test_callback_decision_maker(self):
        """Test callback decision maker."""
        def callback(market):
            return MarketDecision(
                market_id=market.get("id", "test"),
                question=market.get("question", "Test"),
                current_probability=market.get("probability", 0.5),
                decision="YES",
                confidence=0.9,
                reasoning="Callback reasoning"
            )
        
        decision_maker = CallbackDecisionMaker(callback)
        
        market = {
            "id": "test123",
            "question": "Will it rain?",
            "probability": 0.6
        }
        
        decision = decision_maker.analyze_market(market)
        
        assert decision.decision == "YES"
        assert decision.confidence == 0.9
        assert decision.reasoning == "Callback reasoning"

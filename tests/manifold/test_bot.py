"""
Tests for the generic ManifoldBot framework.
"""

import pytest
import os
import platform
from manifoldbot.manifold.bot import (
    ManifoldBot, DecisionMaker, MarketDecision, TradingSession,
    CallbackDecisionMaker, RandomDecisionMaker
)


class MockDecisionMaker(DecisionMaker):
    """Test decision maker for unit tests."""
    
    def __init__(self, decision: str = "SKIP", confidence: float = 0.5, reasoning: str = "Test", outcome_type: str = "UNKNOWN"):
        self.decision = decision
        self.confidence = confidence
        self.reasoning = reasoning
        self.outcome_type = outcome_type
    
    def analyze_market(self, market):
        return MarketDecision(
            market_id=market.get("id", "test"),
            question=market.get("question", "Test question"),
            current_probability=market.get("probability", 0.5),
            decision=self.decision,
            confidence=self.confidence,
            reasoning=self.reasoning,
            outcome_type=self.outcome_type
        )


# Skip integration tests on non-macOS systems (like GitHub CI)
skip_if_not_darwin = pytest.mark.skipif(
    platform.system() != "Darwin" or os.getenv("CI") == "true",
    reason="Integration tests only run locally on macOS"
)


class TestManifoldBot:
    """Test cases for ManifoldBot."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_decision_maker = MockDecisionMaker(outcome_type="BINARY")
    
    @skip_if_not_darwin
    def test_bot_init_real(self):
        """Test bot initialization with real API."""
        # Create bot with real API (will use .env file)
        bot = ManifoldBot(
            manifold_api_key=os.getenv("MANIFOLD_API_KEY"),
            decision_maker=self.test_decision_maker
        )
        
        assert bot.writer is not None
        assert bot.reader is not None
        assert bot.decision_maker == self.test_decision_maker
        assert bot.writer.is_authenticated()
    
    @skip_if_not_darwin
    def test_bot_init_with_callback_real(self):
        """Test bot initialization with callback function using real API."""
        # Create callback function
        def test_callback(market):
            return MarketDecision(
                market_id=market.get("id", "test"),
                question=market.get("question", "Test question"),
                current_probability=market.get("probability", 0.5),
                decision="YES",
                confidence=0.8,
                reasoning="Callback test",
                outcome_type="BINARY"
            )
        
        # Create bot with callback
        bot = ManifoldBot(
            manifold_api_key=os.getenv("MANIFOLD_API_KEY"),
            decision_maker=test_callback
        )
        
        assert bot.writer is not None
        assert bot.reader is not None
        assert bot.decision_maker is not None
        assert bot.writer.is_authenticated()
    
    @skip_if_not_darwin
    def test_analyze_market_real(self):
        """Test market analysis with real API."""
        bot = ManifoldBot(
            manifold_api_key=os.getenv("MANIFOLD_API_KEY"),
            decision_maker=self.test_decision_maker
        )
        
        # Get a real market to test with
        markets = bot.reader.get_markets(limit=1)
        if markets:
            market = markets[0]
            decision = bot.analyze_market(market)
            
            assert decision is not None
            assert decision.market_id == market.get("id")
            assert decision.question == market.get("question")
            assert decision.current_probability == market.get("probability", 0.5)
            assert decision.decision in ["YES", "NO", "SKIP"]
            assert 0 <= decision.confidence <= 1
            assert decision.reasoning is not None
    
    @skip_if_not_darwin
    def test_run_on_recent_markets_real(self):
        """Test running bot on recent markets with real API."""
        bot = ManifoldBot(
            manifold_api_key=os.getenv("MANIFOLD_API_KEY"),
            decision_maker=self.test_decision_maker
        )
        
        # Run on a small number of recent markets
        session = bot.run_on_recent_markets(limit=2, bet_amount=1, max_bets=0, username="MikhailTal")  # max_bets=0 to avoid actual betting
        
        assert session is not None
        assert isinstance(session, TradingSession)
        assert session.markets_analyzed >= 0
        assert session.bets_placed == 0  # Should be 0 since max_bets=0
        assert session.initial_balance > 0
        assert session.final_balance == session.initial_balance  # No bets placed
    
    @skip_if_not_darwin
    def test_run_on_user_markets_real(self):
        """Test running bot on user markets with real API."""
        bot = ManifoldBot(
            manifold_api_key=os.getenv("MANIFOLD_API_KEY"),
            decision_maker=self.test_decision_maker
        )
        
        # Run on MikhailTal's markets (should always have some)
        session = bot.run_on_user_markets(username="MikhailTal", limit=2, bet_amount=1, max_bets=0)
        
        assert session is not None
        assert isinstance(session, TradingSession)
        assert session.markets_analyzed >= 0
        assert session.bets_placed == 0  # Should be 0 since max_bets=0
        assert session.initial_balance > 0
        assert session.final_balance == session.initial_balance  # No bets placed
    
    @skip_if_not_darwin
    def test_run_on_monitored_users_real(self):
        """Test running bot on monitored users with real API."""
        bot = ManifoldBot(
            manifold_api_key=os.getenv("MANIFOLD_API_KEY"),
            decision_maker=self.test_decision_maker
        )
        
        # Test with a small subset of users
        test_users = ["MikhailTal"]  # Just one user for testing
        session = bot.run_on_monitored_users(
            usernames=test_users,
            max_bets_per_user=0,  # No bets
            max_total_bets=0,
            markets_per_user=1,  # Just 1 market per user
            filter_metals_only=True
        )
        
        assert session is not None
        assert isinstance(session, TradingSession)
        assert session.markets_analyzed >= 0
        assert session.bets_placed == 0  # Should be 0 since max_bets=0
        assert session.initial_balance > 0
        assert session.final_balance == session.initial_balance  # No bets placed


class TestRandomDecisionMaker:
    """Test cases for RandomDecisionMaker."""
    
    @skip_if_not_darwin
    def test_analyze_market_low_probability(self):
        """Test random decision maker with low probability market."""
        decision_maker = RandomDecisionMaker()
        market = {"id": "test", "question": "Test?", "probability": 0.1}
        
        decision = decision_maker.analyze_market(market)
        
        assert decision.decision in ["YES", "NO", "SKIP"]
        assert 0 <= decision.confidence <= 1
        assert decision.market_id == "test"
    
    @skip_if_not_darwin
    def test_analyze_market_high_probability(self):
        """Test random decision maker with high probability market."""
        decision_maker = RandomDecisionMaker()
        market = {"id": "test", "question": "Test?", "probability": 0.9}
        
        decision = decision_maker.analyze_market(market)
        
        assert decision.decision in ["YES", "NO", "SKIP"]
        assert 0 <= decision.confidence <= 1
        assert decision.market_id == "test"
    
    @skip_if_not_darwin
    def test_analyze_market_middle_probability(self):
        """Test random decision maker with middle probability market."""
        decision_maker = RandomDecisionMaker()
        market = {"id": "test", "question": "Test?", "probability": 0.5}
        
        decision = decision_maker.analyze_market(market)
        
        assert decision.decision in ["YES", "NO", "SKIP"]
        assert 0 <= decision.confidence <= 1
        assert decision.market_id == "test"


class TestCallbackDecisionMaker:
    """Test cases for CallbackDecisionMaker."""
    
    @skip_if_not_darwin
    def test_callback_decision_maker(self):
        """Test callback decision maker."""
        def callback(market):
            return MarketDecision(
                market_id=market.get("id", "test"),
                question=market.get("question", "Test"),
                current_probability=market.get("probability", 0.5),
                decision="YES",
                confidence=0.8,
                reasoning="Callback decision",
                outcome_type="BINARY"
            )
        
        decision_maker = CallbackDecisionMaker(callback)
        market = {"id": "test", "question": "Test?", "probability": 0.5}
        
        decision = decision_maker.analyze_market(market)
        
        assert decision.decision == "YES"
        assert decision.confidence == 0.8
        assert decision.reasoning == "Callback decision"
        assert decision.market_id == "test"
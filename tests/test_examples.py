"""
Tests for example scripts to ensure they are functional.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

# Test the LLM trading bot
def test_llm_trading_bot_import():
    """Test that the LLM trading bot can be imported."""
    from manifoldbot.examples.llm_trading_bot import LLMTradingBot, TradingDecision
    
    # Test TradingDecision dataclass
    decision = TradingDecision(
        market_id="test123",
        question="Test question?",
        current_probability=0.5,
        llm_probability=0.6,
        decision="YES",
        confidence=0.8,
        reasoning="Test reasoning"
    )
    
    assert decision.market_id == "test123"
    assert decision.decision == "YES"
    assert decision.confidence == 0.8

@patch.dict(os.environ, {"MANIFOLD_API_KEY": "test_key", "OPENAI_API_KEY": "test_openai_key"})
@patch('manifoldbot.examples.llm_trading_bot.openai.OpenAI')
@patch('manifoldbot.examples.llm_trading_bot.ManifoldWriter')
def test_llm_trading_bot_init(mock_writer_class, mock_openai):
    """Test LLM trading bot initialization."""
    from manifoldbot.examples.llm_trading_bot import LLMTradingBot
    
    # Mock the writer
    mock_writer = MagicMock()
    mock_writer.is_authenticated.return_value = True
    mock_writer.get_balance.return_value = 100.0
    mock_writer_class.return_value = mock_writer
    
    # Mock OpenAI client
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    # Create bot
    bot = LLMTradingBot(
        manifold_api_key="test_key",
        openai_api_key="test_openai_key",
        min_confidence=0.6
    )
    
    assert bot.min_confidence == 0.6
    assert bot.writer == mock_writer
    assert bot.client == mock_client

@patch.dict(os.environ, {"MANIFOLD_API_KEY": "test_key", "OPENAI_API_KEY": "test_openai_key"})
@patch('manifoldbot.examples.llm_trading_bot.openai.OpenAI')
@patch('manifoldbot.examples.llm_trading_bot.ManifoldWriter')
@patch('manifoldbot.examples.llm_trading_bot.ManifoldReader')
def test_llm_trading_bot_analyze_market(mock_reader_class, mock_writer_class, mock_openai):
    """Test market analysis functionality."""
    from manifoldbot.examples.llm_trading_bot import LLMTradingBot
    
    # Mock the writer
    mock_writer = MagicMock()
    mock_writer.is_authenticated.return_value = True
    mock_writer.get_balance.return_value = 100.0
    mock_writer_class.return_value = mock_writer
    
    # Mock the reader
    mock_reader = MagicMock()
    mock_reader_class.return_value = mock_reader
    
    # Mock OpenAI client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """
PROBABILITY: 70
CONFIDENCE: 80
REASONING: Based on current trends and data
"""
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    # Create bot
    bot = LLMTradingBot(
        manifold_api_key="test_key",
        openai_api_key="test_openai_key",
        min_confidence=0.6
    )
    
    # Test market analysis
    market = {
        "id": "test123",
        "question": "Will it rain tomorrow?",
        "description": "Weather prediction",
        "probability": 0.5
    }
    
    decision = bot.analyze_market(market)
    
    assert decision.market_id == "test123"
    assert decision.llm_probability == 0.7
    assert decision.confidence == 0.8
    assert decision.decision == "YES"  # LLM thinks 70%, market is 50%, so bet YES
    assert "trends and data" in decision.reasoning

@patch.dict(os.environ, {"MANIFOLD_API_KEY": "test_key", "OPENAI_API_KEY": "test_openai_key"})
@patch('manifoldbot.examples.llm_trading_bot.openai.OpenAI')
@patch('manifoldbot.examples.llm_trading_bot.ManifoldWriter')
@patch('manifoldbot.examples.llm_trading_bot.ManifoldReader')
def test_llm_trading_bot_run_on_user_markets(mock_reader_class, mock_writer_class, mock_openai):
    """Test running bot on user markets."""
    from manifoldbot.examples.llm_trading_bot import LLMTradingBot
    
    # Mock the writer
    mock_writer = MagicMock()
    mock_writer.is_authenticated.return_value = True
    mock_writer.get_balance.return_value = 100.0
    mock_writer_class.return_value = mock_writer
    
    # Mock the reader
    mock_reader = MagicMock()
    mock_reader.get_user.return_value = {"id": "user123", "name": "MikhailTal"}
    mock_reader.get_user_markets.return_value = [
        {"id": "market1", "question": "Test question 1", "probability": 0.5},
        {"id": "market2", "question": "Test question 2", "probability": 0.6}
    ]
    mock_reader_class.return_value = mock_reader
    
    # Mock OpenAI client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """
PROBABILITY: 50
CONFIDENCE: 50
REASONING: No strong opinion
"""
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    # Create bot
    bot = LLMTradingBot(
        manifold_api_key="test_key",
        openai_api_key="test_openai_key",
        min_confidence=0.6
    )
    
    # Test running on user markets
    result = bot.run_on_user_markets(username="MikhailTal", limit=2, bet_amount=5, max_bets=1)
    
    # Should have analyzed 2 markets but placed no bets (confidence too low)
    assert result["markets_analyzed"] == 2
    assert result["bets_placed"] == 0
    assert result["initial_balance"] == 100.0
    
    # Verify the reader methods were called
    mock_reader.get_user.assert_called_once_with("MikhailTal")
    mock_reader.get_user_markets.assert_called_once_with("user123", limit=2)

def test_basic_reader_example():
    """Test that basic reader example can be imported."""
    from manifoldbot.examples.basic_reader import main
    # Just test that it can be imported without error
    assert callable(main)

def test_basic_writer_example():
    """Test that basic writer example can be imported."""
    from manifoldbot.examples.basic_writer import main
    # Just test that it can be imported without error
    assert callable(main)

def test_simple_trading_bot_example():
    """Test that simple trading bot example can be imported."""
    from manifoldbot.examples.simple_trading_bot import main
    # Just test that it can be imported without error
    assert callable(main)
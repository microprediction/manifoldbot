"""
LLM Trading Bot for Manifold Markets.

This bot uses an LLM to analyze market questions and decide whether to bet YES or NO
based on whether it thinks the current probability is off by at least 5%.
"""

import os
import time
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

import openai
from manifoldbot import ManifoldReader, ManifoldWriter


@dataclass
class TradingDecision:
    """Represents a trading decision made by the LLM."""
    market_id: str
    question: str
    current_probability: float
    llm_probability: float
    decision: str  # "YES", "NO", or "SKIP"
    confidence: float
    reasoning: str


class LLMTradingBot:
    """Trading bot that uses LLM to make betting decisions."""
    
    def __init__(self, manifold_api_key: str, openai_api_key: str, min_confidence: float = 0.6):
        """
        Initialize the trading bot.
        
        Args:
            manifold_api_key: Manifold Markets API key
            openai_api_key: OpenAI API key
            min_confidence: Minimum confidence threshold for placing bets
        """
        self.reader = ManifoldReader()
        self.writer = ManifoldWriter(api_key=manifold_api_key)
        
        # Set up OpenAI
        openai.api_key = openai_api_key
        self.client = openai.OpenAI(api_key=openai_api_key)
        
        self.min_confidence = min_confidence
        self.logger = logging.getLogger(__name__)
        
        # Verify authentication
        if not self.writer.is_authenticated():
            raise ValueError("Invalid Manifold API key")
        
        self.logger.info(f"Bot initialized with balance: {self.writer.get_balance():.2f} M$")
    
    def analyze_market(self, market: Dict[str, Any]) -> TradingDecision:
        """
        Use LLM to analyze a market and make a trading decision.
        
        Args:
            market: Market data from Manifold API
            
        Returns:
            TradingDecision object
        """
        question = market.get("question", "")
        description = market.get("description", "")
        current_prob = market.get("probability", 0.5)
        market_id = market.get("id", "")
        
        # Create prompt for LLM
        prompt = f"""
You are an expert market analyst. Analyze this prediction market question and determine what you think the true probability should be.

Question: {question}
Description: {description}

Current market probability: {current_prob:.1%}

Please respond with:
1. Your estimated probability (0-100%)
2. Your confidence in this estimate (0-100%)
3. Brief reasoning for your estimate

Format your response as:
PROBABILITY: [your percentage]
CONFIDENCE: [your confidence percentage]
REASONING: [your brief explanation]
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert market analyst. Be objective and data-driven in your analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            llm_response = response.choices[0].message.content.strip()
            
            # Parse the response
            lines = llm_response.split('\n')
            llm_prob = 0.5
            confidence = 0.5
            reasoning = "No reasoning provided"
            
            for line in lines:
                if line.startswith("PROBABILITY:"):
                    try:
                        llm_prob = float(line.split(":")[1].strip().replace("%", "")) / 100
                    except:
                        llm_prob = 0.5
                elif line.startswith("CONFIDENCE:"):
                    try:
                        confidence = float(line.split(":")[1].strip().replace("%", "")) / 100
                    except:
                        confidence = 0.5
                elif line.startswith("REASONING:"):
                    reasoning = line.split(":", 1)[1].strip()
            
            # Make trading decision
            prob_diff = abs(llm_prob - current_prob)
            decision = "SKIP"
            
            if prob_diff >= 0.05 and confidence >= self.min_confidence:  # 5% difference threshold
                if llm_prob > current_prob:
                    decision = "YES"
                else:
                    decision = "NO"
            
            return TradingDecision(
                market_id=market_id,
                question=question,
                current_probability=current_prob,
                llm_probability=llm_prob,
                decision=decision,
                confidence=confidence,
                reasoning=reasoning
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing market {market_id}: {e}")
            return TradingDecision(
                market_id=market_id,
                question=question,
                current_probability=current_prob,
                llm_probability=0.5,
                decision="SKIP",
                confidence=0.0,
                reasoning=f"Error: {str(e)}"
            )
    
    def place_bet_if_decision(self, decision: TradingDecision, bet_amount: int = 10) -> bool:
        """
        Place a bet if the decision is to bet.
        
        Args:
            decision: TradingDecision object
            bet_amount: Amount to bet in M$
            
        Returns:
            True if bet was placed, False otherwise
        """
        if decision.decision == "SKIP":
            return False
        
        try:
            result = self.writer.place_bet(
                market_id=decision.market_id,
                outcome=decision.decision,
                amount=bet_amount
            )
            
            self.logger.info(
                f"Placed {decision.decision} bet of {bet_amount} M$ on: {decision.question[:50]}... "
                f"(Current: {decision.current_probability:.1%}, LLM: {decision.llm_probability:.1%})"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to place bet on {decision.market_id}: {e}")
            return False
    
    def run_on_markets(self, markets: list, bet_amount: int = 10, max_bets: int = 5) -> Dict[str, Any]:
        """
        Run the bot on a list of markets.
        
        Args:
            markets: List of market data
            bet_amount: Amount to bet per market
            max_bets: Maximum number of bets to place
            
        Returns:
            Summary of trading session
        """
        decisions = []
        bets_placed = 0
        initial_balance = self.writer.get_balance()
        
        self.logger.info(f"Analyzing {len(markets)} markets...")
        
        for i, market in enumerate(markets):
            if bets_placed >= max_bets:
                self.logger.info(f"Reached maximum bets limit ({max_bets})")
                break
            
            self.logger.info(f"Analyzing market {i+1}/{len(markets)}: {market.get('question', '')[:50]}...")
            
            # Analyze market
            decision = self.analyze_market(market)
            decisions.append(decision)
            
            # Log decision
            prob_diff = abs(decision.llm_probability - decision.current_probability)
            self.logger.info(
                f"Decision: {decision.decision} | "
                f"Current: {decision.current_probability:.1%} | "
                f"LLM: {decision.llm_probability:.1%} | "
                f"Diff: {prob_diff:.1%} | "
                f"Confidence: {decision.confidence:.1%}"
            )
            
            if decision.decision != "SKIP":
                if self.place_bet_if_decision(decision, bet_amount):
                    bets_placed += 1
                    time.sleep(1)  # Rate limiting
        
        final_balance = self.writer.get_balance()
        
        return {
            "markets_analyzed": len(decisions),
            "bets_placed": bets_placed,
            "initial_balance": initial_balance,
            "final_balance": final_balance,
            "decisions": decisions
        }
    
    def run_on_recent_markets(self, limit: int = 20, bet_amount: int = 10, max_bets: int = 5) -> Dict[str, Any]:
        """
        Run the bot on recent markets.
        
        Args:
            limit: Number of recent markets to analyze
            bet_amount: Amount to bet per market
            max_bets: Maximum number of bets to place
            
        Returns:
            Summary of trading session
        """
        markets = self.reader.get_markets(limit=limit)
        return self.run_on_markets(markets, bet_amount, max_bets)
    
    def run_on_user_markets(self, username: str = "MikhailTal", limit: int = 20, bet_amount: int = 10, max_bets: int = 5) -> Dict[str, Any]:
        """
        Run the bot on markets created by a specific user.
        
        Args:
            username: Username to get markets from (default: "MikhailTal")
            limit: Number of markets to analyze
            bet_amount: Amount to bet per market
            max_bets: Maximum number of bets to place
            
        Returns:
            Summary of trading session
        """
        self.logger.info(f"Getting markets created by user: {username}")
        
        # First, get the user ID from username
        try:
            # Try to get user by username (this might need to be adjusted based on API)
            user = self.reader.get_user(username)
            user_id = user.get("id")
            if not user_id:
                self.logger.error(f"Could not find user ID for username: {username}")
                return {"error": f"User {username} not found"}
        except Exception as e:
            self.logger.error(f"Error getting user {username}: {e}")
            return {"error": f"Error getting user {username}: {e}"}
        
        # Get markets created by this user
        try:
            markets = self.reader.get_user_markets(user_id, limit=limit)
            self.logger.info(f"Found {len(markets)} markets created by {username}")
            return self.run_on_markets(markets, bet_amount, max_bets)
        except Exception as e:
            self.logger.error(f"Error getting markets for user {username}: {e}")
            return {"error": f"Error getting markets for user {username}: {e}"}


def main():
    """Main function to run the trading bot."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get API keys from environment
    manifold_api_key = os.getenv("MANIFOLD_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not manifold_api_key:
        print("Error: MANIFOLD_API_KEY environment variable not set")
        return
    
    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Create and run bot
    try:
        bot = LLMTradingBot(
            manifold_api_key=manifold_api_key,
            openai_api_key=openai_api_key,
            min_confidence=0.6
        )
        
        # Run on recent markets
        print("Running on recent markets...")
        summary = bot.run_on_recent_markets(
            limit=5,  # Analyze 5 recent markets
            bet_amount=5,  # Bet 5 M$ per market
            max_bets=2  # Maximum 2 bets
        )
        
        # Also run on MikhailTal's markets
        print("\nRunning on MikhailTal's markets...")
        tal_summary = bot.run_on_user_markets(
            username="MikhailTal",
            limit=5,  # Analyze 5 of his markets
            bet_amount=5,  # Bet 5 M$ per market
            max_bets=2  # Maximum 2 bets
        )
        
        # Print summary
        print("\n" + "="*50)
        print("TRADING SESSION SUMMARY")
        print("="*50)
        
        # Recent markets summary
        if "error" not in summary:
            print(f"Recent Markets - Analyzed: {summary['markets_analyzed']}, Bets: {summary['bets_placed']}")
        else:
            print(f"Recent Markets - Error: {summary['error']}")
        
        # MikhailTal markets summary
        if "error" not in tal_summary:
            print(f"MikhailTal Markets - Analyzed: {tal_summary['markets_analyzed']}, Bets: {tal_summary['bets_placed']}")
        else:
            print(f"MikhailTal Markets - Error: {tal_summary['error']}")
        
        # Overall balance
        final_balance = tal_summary.get('final_balance', summary.get('final_balance', 0))
        initial_balance = summary.get('initial_balance', 0)
        print(f"Initial balance: {initial_balance:.2f} M$")
        print(f"Final balance: {final_balance:.2f} M$")
        print(f"Balance change: {final_balance - initial_balance:+.2f} M$")
        
        # Show decisions from both sessions
        all_decisions = []
        if "decisions" in summary:
            all_decisions.extend(summary['decisions'])
        if "decisions" in tal_summary:
            all_decisions.extend(tal_summary['decisions'])
        
        if all_decisions:
            print("\nDecisions made:")
            for decision in all_decisions:
                if decision.decision != "SKIP":
                    prob_diff = abs(decision.llm_probability - decision.current_probability)
                    print(f"  {decision.decision}: {decision.question[:40]}... "
                          f"(Diff: {prob_diff:.1%}, Conf: {decision.confidence:.1%})")
        
    except Exception as e:
        print(f"Error running bot: {e}")


if __name__ == "__main__":
    main()

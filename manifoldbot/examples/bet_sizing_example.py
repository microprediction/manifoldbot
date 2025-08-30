"""
Example demonstrating different bet sizing strategies.

This shows how the bot framework now supports intelligent bet sizing
based on confidence, Kelly Criterion, and other strategies.
"""

import os
import logging
from typing import Dict, Any

from manifoldbot import (
    ManifoldBot, DecisionMaker, MarketDecision,
    SimpleRuleDecisionMaker, KellyCriterionDecisionMaker, ConfidenceBasedDecisionMaker
)


class LLMWithBetSizing(DecisionMaker):
    """LLM decision maker that includes bet sizing based on confidence."""
    
    def __init__(self, openai_api_key: str, min_confidence: float = 0.6, base_bet: float = 10.0):
        """
        Initialize LLM decision maker with bet sizing.
        
        Args:
            openai_api_key: OpenAI API key
            min_confidence: Minimum confidence threshold
            base_bet: Base bet amount for 50% confidence
        """
        import openai
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.min_confidence = min_confidence
        self.base_bet = base_bet
    
    def calculate_bet_size(self, confidence: float, probability_diff: float) -> float:
        """
        Calculate bet size based on confidence and probability difference.
        Higher confidence and larger probability difference = bigger bet.
        """
        # Scale bet by confidence (0.5 = base, 1.0 = 3x base)
        confidence_multiplier = 1 + (confidence - 0.5) * 4
        
        # Scale by probability difference (more difference = bigger bet)
        diff_multiplier = 1 + min(probability_diff * 5, 2.0)  # Cap at 3x
        
        bet_amount = self.base_bet * confidence_multiplier * diff_multiplier
        return min(bet_amount, 50.0)  # Cap at 50 M$
    
    def analyze_market(self, market: Dict[str, Any]) -> MarketDecision:
        """Analyze market using GPT-4 with bet sizing."""
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
            bet_amount = None
            
            if prob_diff >= 0.05 and confidence >= self.min_confidence:  # 5% difference threshold
                if llm_prob > current_prob:
                    decision = "YES"
                else:
                    decision = "NO"
                
                # Calculate bet size based on confidence and probability difference
                bet_amount = self.calculate_bet_size(confidence, prob_diff)
            
            return MarketDecision(
                market_id=market_id,
                question=question,
                current_probability=current_prob,
                decision=decision,
                confidence=confidence,
                reasoning=reasoning,
                bet_amount=bet_amount,
                metadata={
                    "llm_probability": llm_prob,
                    "probability_difference": prob_diff,
                    "bet_size_reason": f"Confidence: {confidence:.1%}, Diff: {prob_diff:.1%}"
                }
            )
            
        except Exception as e:
            return MarketDecision(
                market_id=market_id,
                question=question,
                current_probability=current_prob,
                decision="SKIP",
                confidence=0.0,
                reasoning=f"Error: {str(e)}"
            )


def main():
    """Main function demonstrating different bet sizing strategies."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get API keys
    manifold_api_key = os.getenv("MANIFOLD_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not manifold_api_key:
        print("Error: MANIFOLD_API_KEY environment variable not set")
        return
    
    print("=== Bet Sizing Strategies Demo ===\n")
    
    # Example 1: Fixed bet amount (original behavior)
    print("1. Fixed Bet Amount (10 M$ per bet):")
    try:
        bot1 = ManifoldBot(
            manifold_api_key=manifold_api_key,
            decision_maker=SimpleRuleDecisionMaker()
        )
        
        session1 = bot1.run_on_recent_markets(limit=3, bet_amount=10, max_bets=1)
        print(f"   Analyzed: {session1.markets_analyzed}, Bets: {session1.bets_placed}")
        print(f"   Balance change: {session1.final_balance - session1.initial_balance:+.2f} M$")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Example 2: Confidence-based bet sizing
    print("2. Confidence-Based Bet Sizing:")
    try:
        confidence_decision_maker = ConfidenceBasedDecisionMaker(base_bet=5.0, max_bet=30.0)
        bot2 = ManifoldBot(
            manifold_api_key=manifold_api_key,
            decision_maker=confidence_decision_maker
        )
        
        session2 = bot2.run_on_recent_markets(limit=3, max_bets=1)
        print(f"   Analyzed: {session2.markets_analyzed}, Bets: {session2.bets_placed}")
        print(f"   Balance change: {session2.final_balance - session2.initial_balance:+.2f} M$")
        
        # Show bet sizes
        for decision in session2.decisions:
            if decision.decision != "SKIP":
                print(f"   Bet: {decision.bet_amount:.2f} M$ on '{decision.question[:30]}...' "
                      f"(Conf: {decision.confidence:.1%})")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Example 3: LLM with intelligent bet sizing
    if openai_api_key:
        print("3. LLM with Intelligent Bet Sizing:")
        try:
            llm_decision_maker = LLMWithBetSizing(openai_api_key, min_confidence=0.6, base_bet=8.0)
            bot3 = ManifoldBot(
                manifold_api_key=manifold_api_key,
                decision_maker=llm_decision_maker
            )
            
            session3 = bot3.run_on_recent_markets(limit=2, max_bets=1)
            print(f"   Analyzed: {session3.markets_analyzed}, Bets: {session3.bets_placed}")
            print(f"   Balance change: {session3.final_balance - session3.initial_balance:+.2f} M$")
            
            # Show decisions with bet sizes
            for decision in session3.decisions:
                if decision.decision != "SKIP":
                    metadata = decision.metadata or {}
                    print(f"   Bet: {decision.bet_amount:.2f} M$ on '{decision.question[:30]}...'")
                    print(f"   LLM Prob: {metadata.get('llm_probability', 0):.1%}, "
                          f"Market Prob: {decision.current_probability:.1%}")
                    print(f"   Reasoning: {decision.reasoning[:60]}...")
                    print(f"   Bet Size Reason: {metadata.get('bet_size_reason', 'N/A')}")
        
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print("3. LLM with Intelligent Bet Sizing: (Skipped - OPENAI_API_KEY not set)")
    
    print()
    
    # Example 4: Kelly Criterion with Market Impact Limits
    print("4. Kelly Criterion with Market Impact Limits:")
    try:
        kelly_decision_maker = KellyCriterionDecisionMaker(
            kelly_fraction=0.25, 
            max_prob_impact=0.05,  # 5% max probability impact
            min_bet=2.0, 
            max_bet=50.0
        )
        bot4 = ManifoldBot(
            manifold_api_key=manifold_api_key,
            decision_maker=kelly_decision_maker
        )
        
        session4 = bot4.run_on_recent_markets(limit=3, max_bets=1)
        print(f"   Analyzed: {session4.markets_analyzed}, Bets: {session4.bets_placed}")
        print(f"   Balance change: {session4.final_balance - session4.initial_balance:+.2f} M$")
        
        # Show Kelly decisions with market impact info
        for decision in session4.decisions:
            if decision.decision != "SKIP":
                metadata = decision.metadata or {}
                true_prob = metadata.get('true_probability', 0)
                market_subsidy = metadata.get('market_subsidy', 0)
                market_impact = metadata.get('market_impact', 0)
                max_bet_by_impact = metadata.get('max_bet_by_impact', 0)
                
                print(f"   Kelly Bet: {decision.bet_amount:.2f} M$ on '{decision.question[:30]}...'")
                print(f"   True Prob: {true_prob:.1%}, Market Prob: {decision.current_probability:.1%}")
                if market_subsidy > 0:
                    print(f"   Market Subsidy: {market_subsidy:.2f} M$, Max by Impact: {max_bet_by_impact:.2f} M$")
                    print(f"   Market Impact: {market_impact:.1%}")
                else:
                    print(f"   (No subsidy data available)")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== Bet Sizing Summary ===")
    print("1. Fixed Amount: Simple, predictable, but not optimal")
    print("2. Confidence-Based: Scales with confidence and probability difference")
    print("3. LLM + Bet Sizing: Combines AI analysis with intelligent position sizing")
    print("4. Kelly Criterion: Mathematically optimal with market impact limits")
    print("\nKey Features:")
    print("- Fractional Kelly (25% default) for safety")
    print("- Market impact limits (5% max probability change, configurable)")
    print("- Decision makers can specify their own bet amounts")
    print("- Built-in bankroll management and risk controls")


if __name__ == "__main__":
    main()

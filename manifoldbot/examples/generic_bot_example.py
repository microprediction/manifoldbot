"""
Example showing how to use the generic ManifoldBot framework.

This demonstrates different ways to create decision makers:
1. Using inheritance
2. Using callback functions
3. Using built-in decision makers
"""

import os
import logging
from typing import Dict, Any

from manifoldbot import ManifoldBot, DecisionMaker, MarketDecision


class LLMDecisionMaker(DecisionMaker):
    """Decision maker that uses an LLM (GPT-4) to analyze markets."""
    
    def __init__(self, openai_api_key: str, min_confidence: float = 0.6):
        """
        Initialize LLM decision maker.
        
        Args:
            openai_api_key: OpenAI API key
            min_confidence: Minimum confidence threshold
        """
        import openai
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.min_confidence = min_confidence
    
    def analyze_market(self, market: Dict[str, Any]) -> MarketDecision:
        """Analyze market using GPT-4."""
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
            
            return MarketDecision(
                market_id=market_id,
                question=question,
                current_probability=current_prob,
                decision=decision,
                confidence=confidence,
                reasoning=reasoning,
                metadata={"llm_probability": llm_prob, "probability_difference": prob_diff}
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


def simple_callback_decision_maker(market: Dict[str, Any]) -> MarketDecision:
    """
    Simple callback function for decision making.
    
    This is a basic example that bets YES on markets with low probability.
    """
    current_prob = market.get("probability", 0.5)
    question = market.get("question", "")
    market_id = market.get("id", "")
    
    # Simple rule: bet YES if probability is very low
    if current_prob < 0.2:
        decision = "YES"
        confidence = 0.7
        reasoning = f"Probability {current_prob:.1%} seems too low"
    else:
        decision = "SKIP"
        confidence = 0.5
        reasoning = f"Probability {current_prob:.1%} is not low enough"
    
    return MarketDecision(
        market_id=market_id,
        question=question,
        current_probability=current_prob,
        decision=decision,
        confidence=confidence,
        reasoning=reasoning
    )


def main():
    """Main function demonstrating different bot configurations."""
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
    
    print("=== Generic ManifoldBot Framework Demo ===\n")
    
    # Example 1: Using a callback function
    print("1. Bot with callback function decision maker:")
    try:
        bot1 = ManifoldBot(
            manifold_api_key=manifold_api_key,
            decision_maker=simple_callback_decision_maker
        )
        
        session1 = bot1.run_on_recent_markets(limit=3, bet_amount=1, max_bets=1)
        print(f"   Analyzed: {session1.markets_analyzed}, Bets: {session1.bets_placed}")
        print(f"   Balance change: {session1.final_balance - session1.initial_balance:+.2f} M$")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Example 2: Using inheritance (LLM decision maker)
    if openai_api_key:
        print("2. Bot with LLM decision maker:")
        try:
            llm_decision_maker = LLMDecisionMaker(openai_api_key, min_confidence=0.6)
            bot2 = ManifoldBot(
                manifold_api_key=manifold_api_key,
                decision_maker=llm_decision_maker
            )
            
            session2 = bot2.run_on_user_markets(username="MikhailTal", limit=2, bet_amount=1, max_bets=1)
            print(f"   Analyzed: {session2.markets_analyzed}, Bets: {session2.bets_placed}")
            print(f"   Balance change: {session2.final_balance - session2.initial_balance:+.2f} M$")
            
            # Show decisions
            for decision in session2.decisions:
                if decision.decision != "SKIP":
                    print(f"   Decision: {decision.decision} on '{decision.question[:30]}...'")
                    print(f"   Reasoning: {decision.reasoning}")
            
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print("2. Bot with LLM decision maker: (Skipped - OPENAI_API_KEY not set)")
    
    print()
    
    # Example 3: Using built-in simple rule decision maker
    print("3. Bot with built-in simple rule decision maker:")
    try:
        from manifoldbot.manifold.bot import SimpleRuleDecisionMaker
        
        simple_decision_maker = SimpleRuleDecisionMaker(min_probability_diff=0.1, min_confidence=0.7)
        bot3 = ManifoldBot(
            manifold_api_key=manifold_api_key,
            decision_maker=simple_decision_maker
        )
        
        session3 = bot3.run_on_recent_markets(limit=3, bet_amount=1, max_bets=1)
        print(f"   Analyzed: {session3.markets_analyzed}, Bets: {session3.bets_placed}")
        print(f"   Balance change: {session3.final_balance - session3.initial_balance:+.2f} M$")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()

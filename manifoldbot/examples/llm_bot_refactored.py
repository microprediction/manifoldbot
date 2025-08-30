"""
Refactored LLM Trading Bot using the generic ManifoldBot framework.

This shows how the original LLM bot can be simplified using the new framework.
"""

import os
import logging
from typing import Dict, Any

from manifoldbot import ManifoldBot, DecisionMaker, MarketDecision


class LLMDecisionMaker(DecisionMaker):
    """LLM-based decision maker using the generic framework."""
    
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


def main():
    """Main function using the generic bot framework."""
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
    
    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    try:
        # Create LLM decision maker
        llm_decision_maker = LLMDecisionMaker(openai_api_key, min_confidence=0.6)
        
        # Create bot with LLM decision maker
        bot = ManifoldBot(
            manifold_api_key=manifold_api_key,
            decision_maker=llm_decision_maker
        )
        
        # Run on recent markets
        print("Running on recent markets...")
        recent_session = bot.run_on_recent_markets(
            limit=5,
            bet_amount=5,
            max_bets=2
        )
        
        # Run on MikhailTal's markets
        print("\nRunning on MikhailTal's markets...")
        tal_session = bot.run_on_user_markets(
            username="MikhailTal",
            limit=5,
            bet_amount=5,
            max_bets=2
        )
        
        # Print summary
        print("\n" + "="*50)
        print("TRADING SESSION SUMMARY")
        print("="*50)
        
        # Recent markets summary
        if recent_session.errors:
            print(f"Recent Markets - Error: {recent_session.errors[0]}")
        else:
            print(f"Recent Markets - Analyzed: {recent_session.markets_analyzed}, Bets: {recent_session.bets_placed}")
        
        # MikhailTal markets summary
        if tal_session.errors:
            print(f"MikhailTal Markets - Error: {tal_session.errors[0]}")
        else:
            print(f"MikhailTal Markets - Analyzed: {tal_session.markets_analyzed}, Bets: {tal_session.bets_placed}")
        
        # Overall balance
        final_balance = tal_session.final_balance
        initial_balance = recent_session.initial_balance
        print(f"Initial balance: {initial_balance:.2f} M$")
        print(f"Final balance: {final_balance:.2f} M$")
        print(f"Balance change: {final_balance - initial_balance:+.2f} M$")
        
        # Show decisions from both sessions
        all_decisions = recent_session.decisions + tal_session.decisions
        
        if all_decisions:
            print("\nDecisions made:")
            for decision in all_decisions:
                if decision.decision != "SKIP":
                    prob_diff = decision.metadata.get("probability_difference", 0) if decision.metadata else 0
                    print(f"  {decision.decision}: {decision.question[:40]}... "
                          f"(Diff: {prob_diff:.1%}, Conf: {decision.confidence:.1%})")
        
    except Exception as e:
        print(f"Error running bot: {e}")


if __name__ == "__main__":
    main()

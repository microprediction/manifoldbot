"""
Generic Manifold Markets Trading Bot Framework.


"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass

from .reader import ManifoldReader
from .writer import ManifoldWriter
from .lmsr import LMSRCalculator


@dataclass
class MarketDecision:
    """Represents a trading decision for a market."""
    market_id: str
    question: str
    current_probability: float
    decision: str  # "YES", "NO", or "SKIP"
    confidence: float
    reasoning: str
    bet_amount: Optional[float] = None  # Suggested bet amount
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TradingSession:
    """Represents the results of a trading session."""
    markets_analyzed: int
    bets_placed: int
    initial_balance: float
    final_balance: float
    decisions: List[MarketDecision]
    errors: List[str]


class DecisionMaker(ABC):
    """Abstract base class for market decision makers."""
    
    @abstractmethod
    def analyze_market(self, market: Dict[str, Any]) -> MarketDecision:
        """
        Analyze a market and make a trading decision.
        
        Args:
            market: Market data from Manifold API
            
        Returns:
            MarketDecision object
        """
        pass


class ManifoldBot:
    """
    Generic trading bot for Manifold Markets.
    
    This bot can be configured with different decision-making strategies
    and can run on various market sources.
    """
    
    def __init__(
        self,
        manifold_api_key: str,
        decision_maker: Union[DecisionMaker, Callable[[Dict[str, Any]], MarketDecision]],
        timeout: int = 30,
        retry_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the trading bot.
        
        Args:
            manifold_api_key: Manifold Markets API key
            decision_maker: Decision maker instance or callback function
            timeout: Request timeout in seconds
            retry_config: Custom retry configuration
        """
        self.reader = ManifoldReader(timeout=timeout, retry_config=retry_config)
        self.writer = ManifoldWriter(api_key=manifold_api_key, timeout=timeout, retry_config=retry_config)
        
        # Set up decision maker
        if callable(decision_maker):
            self.decision_maker = CallbackDecisionMaker(decision_maker)
        else:
            self.decision_maker = decision_maker
        
        self.logger = logging.getLogger(__name__)
        
        # Verify authentication
        if not self.writer.is_authenticated():
            raise ValueError("Invalid Manifold API key")
        
        self.logger.info(f"Bot initialized with balance: {self.writer.get_balance():.2f} M$")
    
    def analyze_market(self, market: Dict[str, Any]) -> MarketDecision:
        """
        Analyze a market using the configured decision maker.
        
        Args:
            market: Market data from Manifold API
            
        Returns:
            MarketDecision object
        """
        return self.decision_maker.analyze_market(market)
    
    def place_bet_if_decision(self, decision: MarketDecision, default_bet_amount: float = 10) -> bool:
        """
        Place a bet if the decision is to bet.
        
        Args:
            decision: MarketDecision object
            default_bet_amount: Default amount to bet if decision doesn't specify
            
        Returns:
            True if bet was placed, False otherwise
        """
        if decision.decision == "SKIP":
            return False
        
        # Use decision's bet_amount if specified, otherwise use default
        bet_amount = decision.bet_amount if decision.bet_amount is not None else default_bet_amount
        
        # Ensure we have enough balance
        current_balance = self.writer.get_balance()
        if bet_amount > current_balance:
            self.logger.warning(f"Insufficient balance: {current_balance:.2f} M$ < {bet_amount:.2f} M$")
            return False
        
        try:
            result = self.writer.place_bet(
                market_id=decision.market_id,
                outcome=decision.decision,
                amount=bet_amount
            )
            
            self.logger.info(
                f"Placed {decision.decision} bet of {bet_amount:.2f} M$ on: {decision.question[:50]}... "
                f"(Current: {decision.current_probability:.1%}, Conf: {decision.confidence:.1%})"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to place bet on {decision.market_id}: {e}")
            return False
    
    def run_on_markets(
        self,
        markets: List[Dict[str, Any]],
        bet_amount: int = 10,
        max_bets: int = 5,
        delay_between_bets: float = 1.0
    ) -> TradingSession:
        """
        Run the bot on a list of markets.
        
        Args:
            markets: List of market data
            bet_amount: Amount to bet per market
            max_bets: Maximum number of bets to place
            delay_between_bets: Delay between bets in seconds
            
        Returns:
            TradingSession object
        """
        decisions = []
        bets_placed = 0
        errors = []
        initial_balance = self.writer.get_balance()
        
        self.logger.info(f"Analyzing {len(markets)} markets...")
        
        for i, market in enumerate(markets):
            if bets_placed >= max_bets:
                self.logger.info(f"Reached maximum bets limit ({max_bets})")
                break
            
            self.logger.info(f"Analyzing market {i+1}/{len(markets)}: {market.get('question', '')[:50]}...")
            
            try:
                # Analyze market
                decision = self.analyze_market(market)
                decisions.append(decision)
                
                # Log decision
                prob_diff = abs(decision.confidence - decision.current_probability) if hasattr(decision, 'confidence') else 0
                self.logger.info(
                    f"Decision: {decision.decision} | "
                    f"Current: {decision.current_probability:.1%} | "
                    f"Confidence: {decision.confidence:.1%} | "
                    f"Reasoning: {decision.reasoning[:50]}..."
                )
                
                if decision.decision != "SKIP":
                    if self.place_bet_if_decision(decision, bet_amount):
                        bets_placed += 1
                        time.sleep(delay_between_bets)  # Rate limiting
                        
            except Exception as e:
                error_msg = f"Error analyzing market {market.get('id', 'unknown')}: {e}"
                self.logger.error(error_msg)
                errors.append(error_msg)
        
        final_balance = self.writer.get_balance()
        
        return TradingSession(
            markets_analyzed=len(decisions),
            bets_placed=bets_placed,
            initial_balance=initial_balance,
            final_balance=final_balance,
            decisions=decisions,
            errors=errors
        )
    
    def run_on_recent_markets(
        self,
        limit: int = 20,
        bet_amount: int = 10,
        max_bets: int = 5,
        delay_between_bets: float = 1.0,
        username: str = "MikhailTal"
    ) -> TradingSession:
        """
        Run the bot on markets by a specific user (defaults to MikhailTal).
        
        Args:
            limit: Number of markets to analyze (ignored, gets all user markets)
            bet_amount: Amount to bet per market
            max_bets: Maximum number of bets to place
            delay_between_bets: Delay between bets in seconds
            username: Username to get markets from (default: "MikhailTal")
            
        Returns:
            TradingSession object
        """
        # Get all markets by the specified user (defaults to MikhailTal)
        markets = self.reader.get_all_markets(username=username)
        # Limit to the specified number if requested
        if limit and len(markets) > limit:
            markets = markets[:limit]
        return self.run_on_markets(markets, bet_amount, max_bets, delay_between_bets)
    
    def run_on_user_markets(
        self,
        username: str = "MikhailTal",
        limit: int = 20,
        bet_amount: int = 10,
        max_bets: int = 5,
        delay_between_bets: float = 1.0
    ) -> TradingSession:
        """
        Run the bot on markets created by a specific user.
        
        Args:
            username: Username to get markets from (default: "MikhailTal")
            limit: Number of markets to analyze (0 = all user markets)
            bet_amount: Amount to bet per market
            max_bets: Maximum number of bets to place
            delay_between_bets: Delay between bets in seconds
            
        Returns:
            TradingSession object
        """
        self.logger.info(f"Getting markets created by user: {username}")
        
        try:
            # Get all markets created by this user using the working method
            markets = self.reader.get_all_markets(username=username)
            self.logger.info(f"Found {len(markets)} markets created by {username}")
            
            # Limit to the specified number if requested
            if limit and len(markets) > limit:
                markets = markets[:limit]
                self.logger.info(f"Limited to {len(markets)} markets for analysis")
            
            return self.run_on_markets(markets, bet_amount, max_bets, delay_between_bets)
            
        except Exception as e:
            error_msg = f"Error getting markets for user {username}: {e}"
            self.logger.error(error_msg)
            return TradingSession(
                markets_analyzed=0,
                bets_placed=0,
                initial_balance=self.writer.get_balance(),
                final_balance=self.writer.get_balance(),
                decisions=[],
                errors=[error_msg]
            )
    
    def run_on_market_by_slug(
        self,
        slug: str,
        bet_amount: int = 10
    ) -> TradingSession:
        """
        Run the bot on a specific market by slug.
        
        Args:
            slug: Market slug
            bet_amount: Amount to bet
            
        Returns:
            TradingSession object
        """
        try:
            market = self.reader.get_market_by_slug(slug)
            return self.run_on_markets([market], bet_amount, max_bets=1)
        except Exception as e:
            error_msg = f"Error getting market by slug {slug}: {e}"
            self.logger.error(error_msg)
            return TradingSession(
                markets_analyzed=0,
                bets_placed=0,
                initial_balance=self.writer.get_balance(),
                final_balance=self.writer.get_balance(),
                decisions=[],
                errors=[error_msg]
            )


class CallbackDecisionMaker(DecisionMaker):
    """Decision maker that uses a callback function."""
    
    def __init__(self, callback: Callable[[Dict[str, Any]], MarketDecision]):
        """
        Initialize with a callback function.
        
        Args:
            callback: Function that takes market data and returns MarketDecision
        """
        self.callback = callback
    
    def analyze_market(self, market: Dict[str, Any]) -> MarketDecision:
        """Analyze market using the callback function."""
        return self.callback(market)


class RandomDecisionMaker(DecisionMaker):
    """Random decision maker for testing."""
    
    def __init__(self, min_probability_diff: float = 0.05, min_confidence: float = 0.6):
        """
        Initialize with simple rules.
        
        Args:
            min_probability_diff: Minimum probability difference to bet
            min_confidence: Minimum confidence to bet
        """
        self.min_probability_diff = min_probability_diff
        self.min_confidence = min_confidence
    
    def analyze_market(self, market: Dict[str, Any]) -> MarketDecision:
        """
        Simple rule: bet YES if probability < 0.3, NO if > 0.7.
        """
        current_prob = market.get("probability", 0.5)
        question = market.get("question", "")
        market_id = market.get("id", "")
        
        # Simple rule-based decision
        if current_prob < 0.3:
            decision = "YES"
            confidence = 0.8
            reasoning = f"Probability {current_prob:.1%} seems too low"
        elif current_prob > 0.7:
            decision = "NO"
            confidence = 0.8
            reasoning = f"Probability {current_prob:.1%} seems too high"
        else:
            decision = "SKIP"
            confidence = 0.5
            reasoning = f"Probability {current_prob:.1%} is in reasonable range"
        
        return MarketDecision(
            market_id=market_id,
            question=question,
            current_probability=current_prob,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning
        )


class KellyCriterionDecisionMaker(DecisionMaker):
    """Decision maker that uses Kelly Criterion for bet sizing."""
    
    def __init__(
        self, 
        kelly_fraction: float = 0.25, 
        max_prob_impact: float = 0.05,
        min_bet: float = 1.0, 
        max_bet: float = 100.0
    ):
        """
        Initialize Kelly Criterion decision maker.
        
        Args:
            kelly_fraction: Fraction of Kelly bet to use (0.25 = 25% of Kelly, safer)
            max_prob_impact: Maximum probability impact allowed (0.05 = 5% max change)
            min_bet: Minimum bet amount
            max_bet: Maximum bet amount
        """
        self.kelly_fraction = kelly_fraction
        self.max_prob_impact = max_prob_impact
        self.min_bet = min_bet
        self.max_bet = max_bet
    
    def calculate_market_impact(self, bet_amount: float, current_prob: float, market_subsidy: float, outcome: str) -> float:
        """
        Calculate the actual price impact of a bet using proper LMSR math.
        
        Args:
            bet_amount: Amount of the bet
            current_prob: Current market probability
            market_subsidy: Market liquidity parameter
            outcome: "YES" or "NO"
            
        Returns:
            Absolute change in probability (0.0 to 1.0)
        """
        if market_subsidy <= 0 or bet_amount <= 0:
            return 0.0
        
        calculator = LMSRCalculator(market_subsidy)
        return calculator.calculate_market_impact(bet_amount, current_prob, outcome)
    
    def calculate_kelly_bet(self, true_prob: float, market_prob: float, bankroll: float, market_subsidy: float = None) -> float:
        """
        Calculate optimal bet size using Kelly Criterion with market impact limits.
        
        Uses iterative approach to find bet size where Kelly Criterion is satisfied
        with the marginal (posterior) probability after market impact.
        
        Kelly % = (bp - q) / b
        where:
        - b = odds received (1/marginal_prob - 1)
        - p = probability of winning (true_prob)
        - q = probability of losing (1 - true_prob)
        - marginal_prob = probability at the end of the bet (what we actually get)
        """
        if market_prob <= 0 or market_prob >= 1 or true_prob <= 0 or true_prob >= 1:
            return 0.0
        
        # Determine bet direction
        outcome = "YES" if true_prob > market_prob else "NO"
        
        # If no market subsidy, use simple Kelly with current probability
        if not market_subsidy or market_subsidy <= 0:
            b = (1 / market_prob) - 1
            kelly_fraction = (b * true_prob - (1 - true_prob)) / b
            if kelly_fraction <= 0:
                return 0.0
            kelly_bet = kelly_fraction * self.kelly_fraction * bankroll
            return max(self.min_bet, min(kelly_bet, self.max_bet))
        
        # Use iterative approach to find optimal bet size
        # We need to find bet size where Kelly Criterion is satisfied with marginal probability
        calculator = LMSRCalculator(market_subsidy)
        
        # Binary search for optimal bet size
        low, high = 0.0, min(bankroll, self.max_bet)
        
        for _ in range(50):  # More iterations for precision
            mid = (low + high) / 2
            
            # Calculate marginal probability for this bet size
            marginal_prob = calculator.calculate_marginal_probability(mid, market_prob, outcome)
            
            # Calculate Kelly fraction with marginal probability
            b = (1 / marginal_prob) - 1
            kelly_fraction = (b * true_prob - (1 - true_prob)) / b
            
            # Calculate desired bet size based on Kelly
            desired_bet = kelly_fraction * self.kelly_fraction * bankroll
            
            # Check if this bet size respects impact limits
            impact = calculator.calculate_market_impact(mid, market_prob, outcome)
            
            if kelly_fraction <= 0 or impact > self.max_prob_impact:
                # No positive edge or impact too high
                high = mid
            elif abs(mid - desired_bet) < 0.01:  # Close enough
                break
            elif mid < desired_bet:
                low = mid
            else:
                high = mid
        
        bet_amount = max(self.min_bet, min(mid, self.max_bet))
        
        return bet_amount
    
    def _find_max_bet_by_impact(self, current_prob: float, market_subsidy: float, outcome: str, max_impact: float) -> float:
        """
        Find the maximum bet size that doesn't exceed the probability impact limit.
        Uses the LMSR calculator for accurate results.
        """
        calculator = LMSRCalculator(market_subsidy)
        return calculator.find_max_bet_by_impact(current_prob, outcome, max_impact)
    
    def analyze_market(self, market: Dict[str, Any], bankroll: float = 100.0) -> MarketDecision:
        """
        Analyze market and suggest bet size using Kelly Criterion with market impact limits.
        
        Args:
            market: Market data
            bankroll: Current bankroll for Kelly calculation
        """
        current_prob = market.get("probability", 0.5)
        question = market.get("question", "")
        market_id = market.get("id", "")
        market_subsidy = market.get("subsidy", 0)  # Market subsidy for impact calculation
        
        # For this example, we'll use a simple heuristic for true probability
        # In practice, you'd use your model/LLM to estimate this
        if current_prob < 0.3:
            true_prob = 0.4  # Think it's undervalued
            decision = "YES"
            confidence = 0.7
            reasoning = f"Probability {current_prob:.1%} seems undervalued"
        elif current_prob > 0.7:
            true_prob = 0.6  # Think it's overvalued
            decision = "NO"
            confidence = 0.7
            reasoning = f"Probability {current_prob:.1%} seems overvalued"
        else:
            decision = "SKIP"
            confidence = 0.5
            reasoning = f"Probability {current_prob:.1%} is reasonable"
            return MarketDecision(
                market_id=market_id,
                question=question,
                current_probability=current_prob,
                decision=decision,
                confidence=confidence,
                reasoning=reasoning
            )
        
        # Calculate Kelly bet size with market impact limits
        kelly_bet = self.calculate_kelly_bet(true_prob, current_prob, bankroll, market_subsidy)
        
        # Calculate market impact for reporting
        market_impact = self.calculate_market_impact(kelly_bet, current_prob, market_subsidy, decision) if market_subsidy > 0 else 0
        
        return MarketDecision(
            market_id=market_id,
            question=question,
            current_probability=current_prob,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            bet_amount=kelly_bet,
            metadata={
                "true_probability": true_prob,
                "kelly_fraction": self.kelly_fraction,
                "max_prob_impact": self.max_prob_impact,
                "full_kelly_bet": kelly_bet / self.kelly_fraction if self.kelly_fraction > 0 else 0,
                "market_subsidy": market_subsidy,
                "market_impact": market_impact,
                "max_bet_by_impact": market_subsidy * 0.05 if market_subsidy > 0 else None
            }
        )


class ConfidenceBasedDecisionMaker(DecisionMaker):
    """Decision maker that sizes bets based on confidence level."""
    
    def __init__(self, base_bet: float = 10.0, max_bet: float = 100.0):
        """
        Initialize confidence-based decision maker.
        
        Args:
            base_bet: Base bet amount for 50% confidence
            max_bet: Maximum bet amount
        """
        self.base_bet = base_bet
        self.max_bet = max_bet
    
    def calculate_bet_size(self, confidence: float, probability_diff: float, market_subsidy: float = None) -> float:
        """
        Calculate bet size based on confidence and probability difference.
        Also respects 5% market subsidy limit.
        """
        # Scale bet by confidence (0.5 = base, 1.0 = 2x base)
        confidence_multiplier = confidence * 2
        
        # Scale by probability difference (more difference = bigger bet)
        diff_multiplier = min(probability_diff * 10, 2.0)  # Cap at 2x
        
        bet_amount = self.base_bet * confidence_multiplier * diff_multiplier
        
        # Apply market impact limit (5% of subsidy)
        if market_subsidy and market_subsidy > 0:
            max_bet_by_impact = market_subsidy * 0.05  # 5% of subsidy
            bet_amount = min(bet_amount, max_bet_by_impact)
        
        return min(bet_amount, self.max_bet)
    
    def analyze_market(self, market: Dict[str, Any]) -> MarketDecision:
        """
        Analyze market with confidence-based bet sizing and market impact limits.
        """
        current_prob = market.get("probability", 0.5)
        question = market.get("question", "")
        market_id = market.get("id", "")
        market_subsidy = market.get("subsidy", 0)
        
        # Simple rule for demonstration
        if current_prob < 0.3:
            decision = "YES"
            confidence = 0.8
            probability_diff = 0.3 - current_prob
            reasoning = f"Probability {current_prob:.1%} seems too low"
        elif current_prob > 0.7:
            decision = "NO"
            confidence = 0.8
            probability_diff = current_prob - 0.7
            reasoning = f"Probability {current_prob:.1%} seems too high"
        else:
            decision = "SKIP"
            confidence = 0.5
            probability_diff = 0.0
            reasoning = f"Probability {current_prob:.1%} is reasonable"
            return MarketDecision(
                market_id=market_id,
                question=question,
                current_probability=current_prob,
                decision=decision,
                confidence=confidence,
                reasoning=reasoning
            )
        
        # Calculate bet size based on confidence and market impact limits
        bet_amount = self.calculate_bet_size(confidence, probability_diff, market_subsidy)
        
        return MarketDecision(
            market_id=market_id,
            question=question,
            current_probability=current_prob,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            bet_amount=bet_amount,
            metadata={
                "probability_difference": probability_diff,
                "market_subsidy": market_subsidy,
                "max_bet_by_impact": market_subsidy * 0.05 if market_subsidy > 0 else None
            }
        )


class LLMDecisionMaker(DecisionMaker):
    """Decision maker that uses an LLM to analyze markets."""
    
    def __init__(self, openai_api_key: str, min_confidence: float = 0.6, model: str = "gpt-4"):
        """
        Initialize LLM decision maker.
        
        Args:
            openai_api_key: OpenAI API key
            min_confidence: Minimum confidence threshold for placing bets
            model: GPT model to use
        """
        self.openai_api_key = openai_api_key
        self.min_confidence = min_confidence
        self.model = model
    
    def analyze_market(self, market: Dict[str, Any]) -> MarketDecision:
        """
        Use LLM to analyze a market and make a trading decision.
        
        Args:
            market: Market data from Manifold API
            
        Returns:
            MarketDecision object
        """
        from ..ai import analyze_market_with_gpt
        
        question = market.get("question", "")
        description = market.get("description", "")
        current_prob = market.get("probability", 0.5)
        market_id = market.get("id", "")
        
        try:
            result = analyze_market_with_gpt(
                question=question,
                description=description,
                current_probability=current_prob,
                model=self.model,
                api_key=self.openai_api_key
            )
            
            llm_prob = result["llm_probability"]
            confidence = result["confidence"]
            reasoning = result["reasoning"]
            
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
                metadata={
                    "llm_probability": llm_prob,
                    "probability_difference": prob_diff,
                    "model": self.model
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

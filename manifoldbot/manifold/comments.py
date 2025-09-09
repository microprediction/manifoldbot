"""
Comment models and utilities for Manifold Markets.

This module provides dataclasses and utilities for working with comments
in Manifold Markets, including creation, editing, and AI-powered comment generation.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import logging


@dataclass
class Comment:
    """
    Represents a comment for Manifold Markets.
    
    Attributes:
        contractId: The market ID to comment on
        content: The markdown content of the comment
    """
    contractId: str
    content: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert comment to dictionary format for API calls."""
        return asdict(self)

    def validate(self) -> None:
        """Validate comment data."""
        if not self.contractId:
            raise ValueError("Comment must have a contractId")
        if not self.content or not self.content.strip():
            raise ValueError("Comment content cannot be empty")
        if len(self.content) > 10000:  # Manifold's typical comment limit
            raise ValueError("Comment content too long (max 10,000 characters)")


@dataclass
class CommentReply:
    """
    Represents a reply to an existing comment.
    
    Attributes:
        contractId: The market ID
        content: The markdown content of the reply
        replyToCommentId: The ID of the comment being replied to
    """
    contractId: str
    content: str
    replyToCommentId: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert reply to dictionary format for API calls."""
        return asdict(self)

    def validate(self) -> None:
        """Validate reply data."""
        if not self.contractId:
            raise ValueError("Reply must have a contractId")
        if not self.content or not self.content.strip():
            raise ValueError("Reply content cannot be empty")
        if not self.replyToCommentId:
            raise ValueError("Reply must have a replyToCommentId")


class CommentGenerator:
    """
    AI-powered comment generator for market analysis.
    
    This class integrates with the OpenAI client to generate intelligent
    comments based on market data and analysis results.
    """
    
    def __init__(self, openai_client=None):
        """
        Initialize comment generator.
        
        Args:
            openai_client: Optional OpenAI client instance
        """
        self.openai_client = openai_client
        self.logger = logging.getLogger(__name__)

    def generate_analysis_comment(
        self,
        market_question: str,
        current_probability: float,
        analysis_result: Dict[str, Any],
        include_reasoning: bool = True,
        max_length: int = 500
    ) -> str:
        """
        Generate a comment based on market analysis results.
        
        Args:
            market_question: The market question
            current_probability: Current market probability
            analysis_result: Result from AI analysis (from openai_client.analyze_market_with_gpt)
            include_reasoning: Whether to include reasoning in the comment
            max_length: Maximum comment length
            
        Returns:
            Generated comment text in markdown format
        """
        try:
            # Extract key information from analysis
            llm_prob = analysis_result.get('llm_probability', current_probability)
            confidence = analysis_result.get('confidence', 0.5)
            reasoning = analysis_result.get('reasoning', '')
            
            # Calculate probability difference
            prob_diff = abs(llm_prob - current_probability)
            
            # Generate base comment
            comment_parts = []
            
            # Header with probability assessment
            if prob_diff > 0.1:  # Significant difference
                direction = "higher" if llm_prob > current_probability else "lower"
                comment_parts.append(
                    f"📊 **Analysis Update**: My assessment is **{direction}** than the current market price."
                )
            else:
                comment_parts.append("📊 **Analysis**: Market price seems reasonable.")
            
            # Probability details
            comment_parts.append(
                f"- **Current market**: {current_probability:.1%}\n"
                f"- **My estimate**: {llm_prob:.1%}\n"
                f"- **Confidence**: {confidence:.1%}"
            )
            
            # Add reasoning if requested and available
            if include_reasoning and reasoning and reasoning != "No reasoning provided":
                # Truncate reasoning if too long
                if len(reasoning) > max_length - 200:  # Leave room for other parts
                    reasoning = reasoning[:max_length-203] + "..."
                comment_parts.append(f"\n**Reasoning**: {reasoning}")
            
            # Model attribution
            model_used = analysis_result.get('model_used', 'AI')
            comment_parts.append(f"\n*Analysis by {model_used} via ManifoldBot*")
            
            full_comment = "\n".join(comment_parts)
            
            # Ensure comment doesn't exceed max length
            if len(full_comment) > max_length:
                # Truncate reasoning section if present
                if include_reasoning and reasoning:
                    truncated_reasoning = reasoning[:max_length-300] + "..."
                    comment_parts[-2] = f"\n**Reasoning**: {truncated_reasoning}"
                    full_comment = "\n".join(comment_parts)
            
            return full_comment
            
        except Exception as e:
            self.logger.error(f"Failed to generate analysis comment: {e}")
            # Fallback to simple comment
            return (
                f"📊 **Analysis**: {llm_prob:.1%} probability estimate "
                f"(vs {current_probability:.1%} market price)\n\n"
                f"*Analysis by ManifoldBot*"
            )

    def generate_trading_comment(
        self,
        action: str,  # "BUY", "SELL", or "HOLD"
        market_question: str,
        current_probability: float,
        reasoning: str = "",
        amount: Optional[int] = None
    ) -> str:
        """
        Generate a comment explaining a trading action.
        
        Args:
            action: The trading action taken
            market_question: The market question
            current_probability: Current market probability
            reasoning: Reasoning for the action
            amount: Optional amount traded
            
        Returns:
            Generated comment explaining the trade
        """
        try:
            action_emojis = {
                "BUY": "📈",
                "SELL": "📉", 
                "HOLD": "⏸️"
            }
            
            emoji = action_emojis.get(action, "📊")
            action_text = action.lower()
            
            comment_parts = [f"{emoji} **{action} Signal**"]
            
            if amount:
                comment_parts.append(f"Placed {action_text} order for M${amount}")
            else:
                comment_parts.append(f"Market analysis suggests {action_text}")
                
            comment_parts.append(f"Current probability: {current_probability:.1%}")
            
            if reasoning:
                comment_parts.append(f"\n**Analysis**: {reasoning}")
                
            comment_parts.append("\n*Automated trading by ManifoldBot*")
            
            return "\n".join(comment_parts)
            
        except Exception as e:
            self.logger.error(f"Failed to generate trading comment: {e}")
            return f"{emoji} **{action}** at {current_probability:.1%} - *ManifoldBot*"

    def generate_custom_comment(
        self,
        template: str,
        market_question: str,
        current_probability: float,
        **kwargs
    ) -> str:
        """
        Generate a comment using a custom template.
        
        Args:
            template: Comment template with placeholders
            market_question: Market question
            current_probability: Current probability
            **kwargs: Additional template variables
            
        Returns:
            Generated comment with template variables filled
        """
        try:
            template_vars = {
                'market_question': market_question,
                'current_probability': current_probability,
                'current_probability_pct': f"{current_probability:.1%}",
                **kwargs
            }
            
            return template.format(**template_vars)
            
        except Exception as e:
            self.logger.error(f"Failed to generate custom comment: {e}")
            return template  # Return template as-is if formatting fails
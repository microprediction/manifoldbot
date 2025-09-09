"""
Example of using ManifoldBot's AI-powered comment features.

This example demonstrates:
1. Basic comment posting
2. AI-generated analysis comments  
3. Trading update comments
4. Comment management (edit, delete, etc.)
"""

import os
import logging
from manifoldbot import ManifoldWriter, Comment, CommentGenerator, analyze_market_with_gpt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Example usage of ManifoldBot comment features."""
    
    # Initialize writer (requires MANIFOLD_API_KEY environment variable)
    api_key = os.getenv("MANIFOLD_API_KEY")
    if not api_key:
        logger.error("MANIFOLD_API_KEY environment variable required")
        return
    
    writer = ManifoldWriter(api_key=api_key)
    
    # Example market (replace with actual market ID)
    market_id = "example-market-slug"
    market_question = "Will AI achieve AGI by 2030?"
    current_prob = 0.45
    
    try:
        # 1. Basic comment posting
        logger.info("=== Basic Comment Example ===")
        basic_comment = Comment(
            contractId=market_id,
            content="🤖 **ManifoldBot Test**: This is a basic comment posted via the API"
        )
        
        if input("Post basic comment? (y/n): ").lower() == 'y':
            response = writer.post_comment(basic_comment)
            logger.info(f"Posted basic comment: {response.get('id')}")
        
        # 2. Simple convenience method
        logger.info("=== Simple Comment Example ===")
        if input("Post simple comment? (y/n): ").lower() == 'y':
            response = writer.post_simple_comment(
                market_id, 
                "📊 Quick update: Monitoring this market for interesting developments!"
            )
            logger.info(f"Posted simple comment: {response.get('id')}")
        
        # 3. Analysis comment
        logger.info("=== Analysis Comment Example ===")
        if input("Post analysis comment? (y/n): ").lower() == 'y':
            response = writer.post_analysis_comment(
                market_id=market_id,
                probability_estimate=0.55,
                reasoning="Recent advances in large language models suggest faster progress than expected",
                confidence=0.7
            )
            logger.info(f"Posted analysis comment: {response.get('id')}")
        
        # 4. AI-generated comment (requires OpenAI API key)
        logger.info("=== AI-Generated Comment Example ===")
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and input("Post AI-generated comment? (y/n): ").lower() == 'y':
            try:
                response = writer.post_ai_analysis_comment(
                    market_id=market_id,
                    market_question=market_question,
                    market_description="Market about artificial general intelligence timeline",
                    current_probability=current_prob,
                    model="gpt-4",
                    include_reasoning=True
                )
                
                logger.info(f"Posted AI comment: {response['comment_response'].get('id')}")
                logger.info(f"AI analysis result: {response['analysis'].get('success')}")
                
            except Exception as e:
                logger.error(f"AI comment failed: {e}")
        
        # 5. Trading update comment
        logger.info("=== Trading Update Comment Example ===")
        if input("Post trading update comment? (y/n): ").lower() == 'y':
            response = writer.post_trading_update_comment(
                market_id=market_id,
                action="BUY_YES",
                probability_before=current_prob,
                probability_after=current_prob + 0.03,  # Simulated market impact
                amount=25,
                reasoning="Strong momentum in AI development"
            )
            logger.info(f"Posted trading update: {response.get('id')}")
        
        # 6. Get market comments
        logger.info("=== Retrieving Comments Example ===")
        if input("Retrieve market comments? (y/n): ").lower() == 'y':
            try:
                comments = writer.get_market_comments(market_id, limit=5)
                logger.info(f"Retrieved {len(comments)} comments")
                
                for i, comment in enumerate(comments[:3], 1):
                    logger.info(f"Comment {i}: {comment.get('content', '')[:100]}...")
                    
            except Exception as e:
                logger.error(f"Failed to retrieve comments: {e}")
        
        # 7. Comment generator examples
        logger.info("=== Comment Generator Examples ===")
        generator = CommentGenerator()
        
        # Generate analysis comment
        sample_analysis = {
            'llm_probability': 0.65,
            'confidence': 0.8,
            'reasoning': 'Recent breakthroughs in neural architecture and training efficiency',
            'model_used': 'gpt-4'
        }
        
        analysis_comment = generator.generate_analysis_comment(
            market_question=market_question,
            current_probability=current_prob,
            analysis_result=sample_analysis
        )
        
        logger.info("Generated analysis comment:")
        logger.info(analysis_comment)
        
        # Generate trading comment
        trading_comment = generator.generate_trading_comment(
            action="BUY",
            market_question=market_question,
            current_probability=current_prob,
            reasoning="Technical analysis suggests upward trend",
            amount=50
        )
        
        logger.info("Generated trading comment:")
        logger.info(trading_comment)
        
        logger.info("=== Comment Examples Complete ===")
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
        raise


if __name__ == "__main__":
    main()
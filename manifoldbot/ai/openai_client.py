"""
Simple OpenAI call for ManifoldBot.

"""

import os
from typing import Dict, Any, Optional


def analyze_market_with_gpt(
    question: str,
    description: str,
    current_probability: float,
    model: str = "gpt-5",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze a market using GPT.
    
    Args:
        question: Market question
        description: Market description
        current_probability: Current market probability
        model: GPT model to use
        api_key: OpenAI API key (defaults to env var)
        
    Returns:
        Dictionary with analysis results
    """
    try:
        import openai
        
        client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        
        prompt = f"""
Analyze this prediction market and provide your probability estimate.

Question: {question}
Description: {description}
Current market probability: {current_probability:.1%}

Provide your analysis in this exact format:

PROBABILITY: [your percentage]
CONFIDENCE: [your confidence percentage]
REASONING: [your brief explanation]

Be direct and provide the final answer immediately.
"""
        
        # Prepare API call parameters
        params = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a market analyst. Provide direct, concise answers in the requested format."},
                {"role": "user", "content": prompt}
            ]
        }
        
        # Add max_tokens based on model
        if "gpt-5" in model:
            params["max_completion_tokens"] = 2000  # Give GPT-5 plenty of space for reasoning
        else:
            params["max_tokens"] = 300
        
        # GPT-5 doesn't support custom temperature
        if "gpt-5" not in model:
            params["temperature"] = 0.3
        
        response = client.chat.completions.create(**params)
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
        
        return {
            "llm_probability": llm_prob,
            "confidence": confidence,
            "reasoning": reasoning,
            "raw_response": llm_response,
            "model_used": model,
            "success": True
        }
        
    except Exception as e:
        return {
            "llm_probability": 0.5,
            "confidence": 0.0,
            "reasoning": f"Error: {str(e)}",
            "raw_response": "",
            "model_used": model,
            "success": False,
            "error": str(e)
        }

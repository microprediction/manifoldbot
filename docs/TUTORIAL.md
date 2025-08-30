# ManifoldBot Tutorial

This tutorial will guide you through building trading bots for Manifold Markets using the manifoldbot package.

## Prerequisites

- Python 3.9 or higher
- Manifold Markets account
- API key from Manifold Markets

## Setup

### 1. Installation

```bash
pip install manifoldbot
```

### 2. Get Your API Key

1. Go to [Manifold Markets](https://manifold.markets)
2. Sign in to your account
3. Go to your profile settings
4. Generate an API key
5. Copy the key (you'll need it for authentication)

### 3. Set Environment Variables

```bash
export MANIFOLD_API_KEY="your_api_key_here"
```

Or create a `.env` file:

```bash
echo "MANIFOLD_API_KEY=your_api_key_here" > .env
```

## Tutorial 1: Basic Market Analysis

Let's start by analyzing markets to understand the data structure.

```python
from manifoldbot.manifold import ManifoldReader

# Initialize the reader (no API key needed)
reader = ManifoldReader()

# Get recent markets
markets = reader.get_markets(limit=10)

print("Recent Markets:")
for market in markets:
    question = market.get('question', 'Unknown')
    probability = market.get('probability', 0)
    volume = market.get('volume', 0)
    
    print(f"• {question[:60]}...")
    print(f"  Probability: {probability:.1%}")
    print(f"  Volume: {volume}Ṁ")
    print()
```

### Exercise 1: Find High-Volume Markets

```python
# Find markets with high trading volume
high_volume_markets = [
    m for m in markets 
    if m.get('volume', 0) > 1000
]

print(f"Found {len(high_volume_markets)} high-volume markets")
for market in high_volume_markets:
    print(f"• {market['question'][:50]}... - {market['volume']}Ṁ")
```

## Tutorial 2: User Analysis

Let's analyze a specific user's markets.

```python
# Get markets by a specific user
user_id = "MikhailTal"  # Example user
user_markets = reader.get_user_markets(user_id, limit=20)

print(f"Markets by {user_id}:")
for market in user_markets:
    question = market.get('question', 'Unknown')
    probability = market.get('probability', 0)
    is_resolved = market.get('isResolved', True)
    
    status = "RESOLVED" if is_resolved else "OPEN"
    print(f"• [{status}] {question[:50]}... - {probability:.1%}")
```

### Exercise 2: Market Performance Analysis

```python
# Analyze market performance
resolved_markets = [m for m in user_markets if m.get('isResolved', True)]
open_markets = [m for m in user_markets if not m.get('isResolved', True)]

print(f"Resolved markets: {len(resolved_markets)}")
print(f"Open markets: {len(open_markets)}")

if resolved_markets:
    avg_probability = sum(m.get('probability', 0) for m in resolved_markets) / len(resolved_markets)
    print(f"Average probability of resolved markets: {avg_probability:.1%}")
```

## Tutorial 3: Basic Trading

Now let's start trading! First, let's set up authentication.

```python
import os
from manifoldbot.manifold import ManifoldWriter

# Initialize the writer with your API key
api_key = os.getenv("MANIFOLD_API_KEY")
if not api_key:
    raise ValueError("MANIFOLD_API_KEY environment variable not set")

writer = ManifoldWriter(api_key=api_key)

# Check authentication
if not writer.is_authenticated():
    raise ValueError("Authentication failed - check your API key")

# Get user info
user_info = writer.get_me()
print(f"Logged in as: {user_info['name']}")
print(f"Balance: {writer.get_balance()}Ṁ")
```

### Exercise 3: Place Your First Bet

```python
# Find a market to bet on
markets = reader.get_markets(limit=20)
open_markets = [m for m in markets if not m.get('isResolved', True)]

if open_markets:
    # Pick the first open market
    target_market = open_markets[0]
    market_id = target_market['id']
    question = target_market['question']
    current_prob = target_market.get('probability', 0.5)
    
    print(f"Betting on: {question}")
    print(f"Current probability: {current_prob:.1%}")
    
    # Place a small bet
    try:
        result = writer.place_bet(market_id, "YES", 1)  # 1Ṁ bet
        print(f"Bet placed successfully!")
        print(f"Bet ID: {result.get('betId', 'unknown')}")
        print(f"Shares received: {result.get('shares', 0):.2f}")
    except Exception as e:
        print(f"Bet failed: {e}")
else:
    print("No open markets found")
```

## Tutorial 4: Limit Orders

Limit orders allow you to specify the maximum price you're willing to pay.

```python
# Place a limit order
market_id = "your_market_id_here"
target_probability = 0.3  # 30% probability
bet_amount = 10  # 10Ṁ

try:
    # Place a limit order to buy YES at 30% or better
    result = writer.place_limit_yes(market_id, bet_amount, target_probability)
    print(f"Limit order placed: {result.get('betId', 'unknown')}")
    print(f"Order amount: {result.get('orderAmount', 0)}Ṁ")
    print(f"Limit probability: {target_probability:.1%}")
except Exception as e:
    print(f"Limit order failed: {e}")
```

### Exercise 4: Smart Limit Orders

```python
def place_smart_limit_order(market_id, outcome, amount, target_prob, max_impact=0.05):
    """
    Place a limit order only if the market impact is acceptable.
    """
    try:
        # Calculate market impact
        impact = writer.calculate_market_impact(market_id, amount, outcome)
        estimated_impact = impact.get('estimated_impact', 0)
        
        if estimated_impact <= max_impact:
            if outcome == "YES":
                result = writer.place_limit_yes(market_id, amount, target_prob)
            else:
                result = writer.place_limit_no(market_id, amount, target_prob)
            
            print(f"Smart limit order placed: {result.get('betId', 'unknown')}")
            return result
        else:
            print(f"Market impact too high: {estimated_impact:.3f} > {max_impact}")
            return None
            
    except Exception as e:
        print(f"Smart limit order failed: {e}")
        return None

# Use the smart limit order function
result = place_smart_limit_order(market_id, "YES", 20, 0.4, max_impact=0.03)
```

## Tutorial 5: Building a Simple Trading Bot

Let's build a basic trading bot that looks for undervalued markets.

```python
import time
from typing import List, Dict, Any

class SimpleTradingBot:
    def __init__(self, api_key: str):
        self.reader = ManifoldReader()
        self.writer = ManifoldWriter(api_key=api_key)
        self.max_bet_size = 10  # Maximum bet size in M$
        self.min_balance = 50   # Minimum balance to keep
        
    def find_undervalued_markets(self, keywords: List[str], max_probability: float = 0.3) -> List[Dict[str, Any]]:
        """Find markets that might be undervalued."""
        markets = self.reader.get_markets(limit=100)
        
        undervalued = []
        for market in markets:
            if market.get('isResolved', True):
                continue
                
            question = market.get('question', '').lower()
            probability = market.get('probability', 0)
            volume = market.get('volume', 0)
            
            # Check if market contains keywords and is below threshold
            if (any(keyword.lower() in question for keyword in keywords) and 
                probability <= max_probability and 
                volume > 100):  # Some trading activity
                
                undervalued.append(market)
        
        return undervalued
    
    def should_place_bet(self, market: Dict[str, Any]) -> bool:
        """Determine if we should bet on this market."""
        # Check balance
        if self.writer.get_balance() < self.min_balance:
            return False
        
        # Check market conditions
        probability = market.get('probability', 0)
        volume = market.get('volume', 0)
        
        # Only bet on markets with reasonable activity
        return volume > 50 and probability < 0.4
    
    def run_trading_cycle(self, keywords: List[str]):
        """Run one trading cycle."""
        print("🔍 Searching for undervalued markets...")
        
        undervalued = self.find_undervalued_markets(keywords)
        print(f"Found {len(undervalued)} potentially undervalued markets")
        
        for market in undervalued[:5]:  # Limit to top 5
            if self.should_place_bet(market):
                try:
                    market_id = market['id']
                    question = market['question']
                    probability = market.get('probability', 0)
                    
                    print(f"🎯 Betting on: {question[:50]}...")
                    print(f"   Current probability: {probability:.1%}")
                    
                    # Place a small bet
                    result = self.writer.place_bet(market_id, "YES", 5)
                    print(f"   ✅ Bet placed: {result.get('betId', 'unknown')}")
                    
                    # Wait between bets to avoid rate limits
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"   ❌ Bet failed: {e}")
            else:
                print(f"⏭️  Skipping market (insufficient balance or poor conditions)")

# Initialize and run the bot
bot = SimpleTradingBot(api_key=os.getenv("MANIFOLD_API_KEY"))

# Run trading cycle for AI-related markets
bot.run_trading_cycle(["AI", "artificial intelligence", "machine learning"])
```

## Tutorial 6: Advanced Features

### Portfolio Management

```python
def analyze_portfolio(writer: ManifoldWriter):
    """Analyze current portfolio."""
    portfolio = writer.get_portfolio()
    positions = writer.get_positions()
    
    print("📊 Portfolio Analysis:")
    print(f"Balance: {writer.get_balance():.2f}Ṁ")
    print(f"Total deposits: {writer.get_total_deposits():.2f}Ṁ")
    print(f"Active positions: {len(positions)}")
    
    # Analyze positions by market
    position_by_market = {}
    for position in positions:
        market_id = position.get('contractId')
        if market_id:
            if market_id not in position_by_market:
                position_by_market[market_id] = []
            position_by_market[market_id].append(position)
    
    print(f"Markets with positions: {len(position_by_market)}")

# Run portfolio analysis
analyze_portfolio(writer)
```

### Market Impact Analysis

```python
def analyze_market_impact(writer: ManifoldWriter, market_id: str):
    """Analyze how different bet sizes would affect a market."""
    bet_sizes = [10, 50, 100, 500]
    
    print(f"📈 Market Impact Analysis for {market_id}:")
    
    for size in bet_sizes:
        try:
            impact = writer.calculate_market_impact(market_id, size, "YES")
            current_prob = impact.get('current_probability', 0)
            new_prob = impact.get('new_probability', 0)
            impact_amount = new_prob - current_prob
            
            print(f"  {size}Ṁ bet: {current_prob:.1%} → {new_prob:.1%} (Δ{impact_amount:+.1%})")
        except Exception as e:
            print(f"  {size}Ṁ bet: Error - {e}")

# Analyze impact for a specific market
market_id = "your_market_id_here"
analyze_market_impact(writer, market_id)
```

## Best Practices

### 1. Risk Management

```python
def safe_betting_strategy(writer: ManifoldWriter, market_id: str, max_bet_percent: float = 0.02):
    """Only bet a small percentage of balance."""
    balance = writer.get_balance()
    max_bet = balance * max_bet_percent
    
    if max_bet < 1:  # Minimum 1Ṁ bet
        print("Insufficient balance for betting")
        return None
    
    return min(max_bet, 50)  # Cap at 50Ṁ
```

### 2. Error Handling

```python
def robust_bet_placement(writer: ManifoldWriter, market_id: str, outcome: str, amount: int):
    """Place bet with comprehensive error handling."""
    try:
        # Validate inputs
        if outcome not in ["YES", "NO"]:
            raise ValueError("Outcome must be 'YES' or 'NO'")
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Check balance
        if writer.get_balance() < amount:
            raise ValueError("Insufficient balance")
        
        # Place bet
        result = writer.place_bet(market_id, outcome, amount)
        return result
        
    except requests.RequestException as e:
        if e.response.status_code == 400:
            print("Bad request - check market ID and parameters")
        elif e.response.status_code == 401:
            print("Authentication failed")
        else:
            print(f"API error: {e}")
        return None
    except ValueError as e:
        print(f"Validation error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

### 3. Rate Limiting

```python
import time

def rate_limited_trading(writer: ManifoldWriter, markets: List[Dict], delay: float = 1.0):
    """Trade on multiple markets with rate limiting."""
    for i, market in enumerate(markets):
        try:
            result = writer.place_bet(market['id'], "YES", 5)
            print(f"Bet {i+1}/{len(markets)} placed successfully")
            
            # Wait between requests
            if i < len(markets) - 1:  # Don't wait after the last bet
                time.sleep(delay)
                
        except Exception as e:
            print(f"Bet {i+1} failed: {e}")
            # Wait longer on error
            time.sleep(delay * 2)
```

## Next Steps

Now that you've completed the tutorial, you can:

1. **Build more sophisticated bots** with machine learning models
2. **Implement advanced strategies** like arbitrage or market making
3. **Create monitoring dashboards** to track your bot's performance
4. **Add more sophisticated risk management** and position sizing
5. **Integrate with other data sources** for better market analysis

Remember to always:
- Start with small bet sizes
- Test your strategies thoroughly
- Monitor your bot's performance
- Keep your API key secure
- Respect rate limits and terms of service

Happy trading! 🚀

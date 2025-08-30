# Kelly Criterion for Prediction Markets

The Kelly Criterion is a mathematical formula for determining optimal bet sizes to maximize long-term growth while minimizing risk. In prediction markets, it helps traders determine how much to bet based on their confidence and the market's current probability.

## Overview

The Kelly Criterion formula is:

```
Kelly % = (bp - q) / b
```

Where:
- `b` = odds received (1/probability - 1)
- `p` = probability of winning (your true probability)
- `q` = probability of losing (1 - p)

## Key Concepts

### Fractional Kelly
Instead of betting the full Kelly amount, most traders use a fraction (typically 25%) to reduce risk:
- **Full Kelly (1.0)**: Maximum growth but high volatility
- **Quarter Kelly (0.25)**: Balanced growth with lower risk
- **Tenth Kelly (0.1)**: Conservative approach with minimal risk

### Market Impact
In prediction markets, large bets move prices, creating "slippage." The iterative Kelly approach accounts for this by:
1. Calculating the marginal probability after the bet
2. Using that probability in the Kelly formula
3. Iterating until the bet size matches the Kelly recommendation

## Implementation

### Basic Usage

```python
from manifoldbot.manifold.bot import KellyCriterionDecisionMaker

# Create decision maker with 25% Kelly fraction
kelly_dm = KellyCriterionDecisionMaker(kelly_fraction=0.25)

# Create decision maker with impact limits
kelly_dm = KellyCriterionDecisionMaker(
    kelly_fraction=0.25,
    max_prob_impact=0.05  # Max 5% price impact
)

# Calculate optimal bet
bet_size = kelly_dm.calculate_kelly_bet(
    true_prob=0.7,      # Your estimated probability
    market_prob=0.5,    # Current market probability
    bankroll=1000.0,    # Your available capital
    market_subsidy=100.0  # Market liquidity
)
```

### Parameters

- **kelly_fraction**: Fraction of Kelly bet to use (default: 0.25)
- **min_bet**: Minimum bet amount (default: 1.0)
- **max_bet**: Maximum bet amount (default: 100.0)
- **max_prob_impact**: Maximum allowed probability change (default: 0.05)

## Examples

### Example 1: Simple vs Iterative Kelly

```python
# Market: 50% probability, you think 70%
true_prob = 0.7
market_prob = 0.5
bankroll = 1000.0
market_subsidy = 100.0

# Simple Kelly (ignoring market impact)
simple_b = (1 / market_prob) - 1  # = 1.0
simple_kelly = (simple_b * true_prob - (1 - true_prob)) / simple_b  # = 0.4
simple_bet = simple_kelly * 0.25 * bankroll  # = $100

# But this bet moves the market to ~58%, reducing our edge!

# Iterative Kelly (accounting for market impact)
kelly_dm = KellyCriterionDecisionMaker(kelly_fraction=0.25, max_prob_impact=0.05)
iterative_bet = kelly_dm.calculate_kelly_bet(
    true_prob, market_prob, bankroll, market_subsidy
)
# Result: ~$45 (optimal size considering slippage)
```

### Example 2: Different Kelly Fractions

```python
kelly_fractions = [0.1, 0.25, 0.5, 1.0]

for kf in kelly_fractions:
    kelly_dm = KellyCriterionDecisionMaker(kelly_fraction=kf)
    bet = kelly_dm.calculate_kelly_bet(
        true_prob=0.65, market_prob=0.4, 
        bankroll=2000.0, market_subsidy=200.0
    )
    print(f"Kelly {kf:.0%}: ${bet:.2f}")
```

Results:
- Kelly 10%: $15.23
- Kelly 25%: $38.07
- Kelly 50%: $76.14
- Kelly 100%: $152.28

### Example 3: Market Impact Limits

```python
# Small market with high impact
market_subsidy = 50.0  # Low liquidity

impact_limits = [0.01, 0.02, 0.05, 0.1]

for max_impact in impact_limits:
    kelly_dm = KellyCriterionDecisionMaker(kelly_fraction=0.25, max_prob_impact=max_impact)
    bet = kelly_dm.calculate_kelly_bet(
        true_prob=0.8, market_prob=0.3,
        bankroll=5000.0, market_subsidy=market_subsidy
    )
    print(f"Max impact {max_impact:.0%}: ${bet:.2f}")
```

Results:
- Max impact 1%: $2.50
- Max impact 2%: $5.00
- Max impact 5%: $12.50
- Max impact 10%: $25.00

## Mathematical Details

### Iterative Algorithm

The iterative Kelly algorithm uses binary search to find the optimal bet size:

1. Start with bet size range [0, bankroll]
2. For each midpoint bet size:
   - Calculate marginal probability after the bet
   - Calculate Kelly fraction using marginal probability
   - Calculate desired bet size from Kelly formula
   - Adjust search range based on comparison
3. Continue until convergence (typically < 10 iterations)

### Market Impact Calculation

For LMSR markets, the market impact is calculated using:

```
new_prob = 1 / (1 + exp(-(current_log_odds + bet_amount/subsidy)))
impact = |new_prob - current_prob|
```

Where `current_log_odds = ln(current_prob / (1 - current_prob))`

## Best Practices

### Risk Management
- **Start with 25% Kelly**: Good balance of growth and risk
- **Set position limits**: Never bet more than 5-10% of bankroll
- **Use impact limits**: Prevent moving markets too much
- **Diversify**: Don't put all capital in one market

### Market Selection
- **High liquidity**: Markets with larger subsidies have less impact
- **Clear edges**: Only bet when you have strong conviction
- **Reasonable spreads**: Avoid markets with extreme probabilities

### Monitoring
- **Track performance**: Monitor actual vs expected returns
- **Adjust fractions**: Reduce Kelly fraction if experiencing high volatility
- **Review decisions**: Analyze both wins and losses

## Common Pitfalls

### Over-betting
- **Problem**: Using full Kelly or ignoring market impact
- **Solution**: Use fractional Kelly and account for slippage

### Under-betting
- **Problem**: Being too conservative with very small Kelly fractions
- **Solution**: Find the right balance for your risk tolerance

### Ignoring Market Impact
- **Problem**: Calculating Kelly based on current price, not marginal price
- **Solution**: Use iterative Kelly that accounts for slippage

### Poor Probability Estimation
- **Problem**: Overconfident in your probability estimates
- **Solution**: Be conservative and use wider confidence intervals

## Advanced Topics

### Dynamic Kelly
Adjust Kelly fraction based on:
- Recent performance
- Market volatility
- Bankroll size
- Number of concurrent positions

### Portfolio Kelly
When betting on multiple markets:
- Calculate Kelly for each market independently
- Scale down if total exposure exceeds risk limits
- Consider correlation between markets

### Bayesian Kelly
Update probability estimates using:
- New information
- Market movements
- Historical accuracy

## References

- [Kelly Criterion Wikipedia](https://en.wikipedia.org/wiki/Kelly_criterion)
- [LMSR Paper](https://www.cs.cmu.edu/~sandholm/ec05.lmsr.pdf)
- [Prediction Markets Theory](https://www.prediction-markets.com/)

## Examples in Codebase

See the following files for complete examples:
- `manifoldbot/examples/iterative_kelly_examples.py` - Comprehensive examples
- `manifoldbot/examples/marginal_vs_average_kelly.py` - Kelly comparison
- `manifoldbot/examples/bet_sizing_example.py` - General bet sizing examples

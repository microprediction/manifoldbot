#!/usr/bin/env python3
"""
Example bot that monitors a list of users.

This bot will cycle through the specified users and analyze their recent markets.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import manifoldbot
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from manifoldbot.manifold.bot import ManifoldBot
from manifoldbot.manifold.decision_makers import SimpleDecisionMaker


def main():
    """Run the bot on a list of users."""
    
    # Get API key from environment
    api_key = os.getenv("MANIFOLD_API_KEY")
    if not api_key:
        print("❌ Error: MANIFOLD_API_KEY environment variable not set")
        print("Please set your Manifold API key:")
        print("export MANIFOLD_API_KEY='your_api_key_here'")
        return
    
    # Load users from config file
    config_path = Path(__file__).parent / "monitored_users.yaml"
    if config_path.exists():
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        users_to_monitor = config.get('users', [])
        print(f"📋 Loaded {len(users_to_monitor)} users from config")
    else:
        # Fallback to default list
        users_to_monitor = [
            "BoltonBailey",    # macro/industrial questions tied to lithium production rankings
            "JoshDreckmeyr",   # frequent, clearly resolved gold (XAU/USD) price markets
            "postjawline",     # materials/science angles that touch copper
            "MikhailTal",      # chess and other markets
            "trevortaylor",    # additional user
            "neweconomicplan", # electric vehicles, energy policy, automotive, politics
            "kian_spire",      # technology, cars, electric vehicles, global EV trends
            "mndrix",          # business, law & order, Tesla, US policy, cars
            "Philip3773733"    # technology, Tesla, cars, Norway, EV adoption
        ]
        print("📋 Using default user list (no config file found)")
    
    # Create a simple decision maker
    decision_maker = SimpleDecisionMaker(
        default_probability=0.6,
        confidence_threshold=0.7,
        max_bet_amount=5.0
    )
    
    # Initialize the bot
    try:
        bot = ManifoldBot(
            manifold_api_key=api_key,
            decision_maker=decision_maker
        )
    except Exception as e:
        print(f"❌ Error initializing bot: {e}")
        return
    
    print("🤖 Bot initialized successfully!")
    print(f"💰 Current balance: {bot.writer.get_balance():.2f} M$")
    print(f"👥 Monitoring users: {', '.join(users_to_monitor)}")
    print()
    
    # Run on the list of users
    try:
        session = bot.run_on_monitored_users(
            usernames=users_to_monitor,
            bet_amount=2,
            max_bets_per_user=1,
            max_total_bets=4,
            delay_between_bets=3.0,
            markets_per_user=3,
            filter_metals_only=True  # Only trade on metals/commodities markets
        )
        
        # Print results
        print("\n📊 Session Results:")
        print(f"  Markets analyzed: {session.markets_analyzed}")
        print(f"  Bets placed: {session.bets_placed}")
        print(f"  Balance change: {session.initial_balance:.2f} → {session.final_balance:.2f} M$")
        
        if session.errors:
            print(f"\n⚠️  Errors encountered:")
            for error in session.errors:
                print(f"  • {error}")
        
        if session.decisions:
            print(f"\n🎯 Decisions made:")
            for decision in session.decisions:
                if decision.decision != "SKIP":
                    print(f"  • {decision.decision} on: {decision.question[:50]}...")
                    print(f"    Confidence: {decision.confidence:.1%}, Reasoning: {decision.reasoning[:100]}...")
        
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        return
    
    print("\n✅ Bot run completed!")


if __name__ == "__main__":
    main()

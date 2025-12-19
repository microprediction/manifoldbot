
# Alternatives / Derivative Manifold Bots

This repository (`microprediction/manifoldbot`) is a general-purpose Python package for building Manifold trading bots, with examples such as an LLM trading bot that compares GPT-generated probabilities to market prices and bets using fractional Kelly sizing.

Below are community-built bots that take this pattern in different directions. For each one, the focus is on **what’s novel relative to `manifoldbot`** rather than just re-implementing the same thing.

---

## `better_manifold_bot` (sachin-detrax)

**Repo:** https://github.com/sachin-detrax/better_manifold_bot

**What it is:** A “souped-up” Manifold bot using a multi-signal ensemble (historical performance, market microstructure, and an OpenAI LLM) to produce a single “true probability,” plus serious tooling for performance analysis.

**Novelty vs `manifoldbot`:**

- Multi-signal ensemble combining historical bias, order-book microstructure, and structured LLM forecasts
- Variance-aware LLM usage (multiple runs + disagreement penalty)
- Dedicated ensemble decision layer with edge calculation
- Advanced fractional Kelly with bankroll caps
- Built-in performance graphs and detailed rationale logging
- Configurable creator targeting (default: `MikhailTal`)

**Best for:** Users who want a research-grade ensemble bot with excellent observability.

---

## `ppbot-ai` (prathameshpatrawale)

**Repo:** https://github.com/prathameshpatrawale/ppbot-ai

**What it is:** Contest-oriented bot built for the Manifold Featured Challenge, trading only `MikhailTal` markets.

**Novelty vs `manifoldbot`:**

- Pure technical strategy (no LLM): mean-reversion + momentum + liquidity filters
- Automatic simulation/real mode switching based on API key presence
- Simple PnL logging and one-click cumulative profit plotting
- Very clean, minimal modular structure

**Best for:** Lightweight non-LLM bots with quick setup and basic analytics.

---

## `Manifoldbot-Ultra` (Sbha8282)

**Repo:** https://github.com/Sbha8282/Manifoldbot-Ultra

**What it is:** Packaged, modular bot designed as a proper Python package with dry-run by default.

**Novelty vs `manifoldbot`:**

- Modern `src/` layout with tests (Python 3.10+)
- Session-cookie betting support (`MANIFOLD_SESSION_COOKIE`)
- Safe-by-default (`DRY_RUN=true`)
- Optional LLM layer (falls back to heuristics)
- Strict creator targeting via env var

**Best for:** Anyone wanting a clean, production-style package skeleton.

---

## `TalOS-Manifold-Bot` (rodriguezramirezederdominic-web)

**Repo:** https://github.com/rodriguezramirezederdominic-web/TalOS-Manifold-Bot

**What it is:** Agentic bot using GPT-4 for reference-class reasoning and fractional Kelly sizing.

**Novelty vs `manifoldbot`:**

- Fully agentic LLM workflow (not just prompt → probability)
- Explicit fractional Kelly module for risk-of-ruin control
- Clear separation: trading loop, brain, and money-management files
- Hard-coded focus on a single creator

**Best for:** Studying readable “LLM-as-brain + proper bankroll management” designs.

---

## `Best-Open-Source-Judgmental-Prediction-Python-Repository` (“Afaq”)

**Repo:** https://github.com/H-tech-AFAQ-CEO/Best-Open-Source-Judgmental-Prediction-Python-Repository

**What it is:** Polished modular bot with both simple and LLM strategies.

**Novelty vs `manifoldbot`:**

- Full type hints, strong error handling, and logging
- Strategy base class with `SimpleStrategy` and `LLMStrategy`
- Integrated backtesting script
- Risk controls and cooldown logic
- Designed to be PR-ready for upstream `manifoldbot`

**Best for:** Clean, typed codebases suitable for contribution or extension.

---

## `bot-` (“Joshi-Bot”, 101jayjoshi-sudo)

**Repo:** https://github.com/101jayjoshi-sudo/bot-

**What it is:** Minimal scaffold focused on `MikhailTal` markets.

**Novelty vs `manifoldbot`:**

- Extremely lightweight — meant as a clean starting template
- Heuristics-first with hooks for local models (not tied to OpenAI)
- Real bets disabled by default (`PLACE_BETS=true` required)
- Explicit username → user-ID resolution step

**Best for:** Quick hacking and plugging in custom/local models.

---

## `Manifold-Markets-Trading-Bot` (blackXmask)

**Repo:** https://github.com/blackXmask/Manifold-Markets-Trading-Bot

**What it is:** Full-featured trading dashboard with Streamlit GUI.

**Novelty vs `manifoldbot`:**

- Rich Streamlit app with live monitoring, portfolio analytics, correlation heatmaps
- Portfolio-level optimization and diversification logic
- Built-in arbitrage detection
- Advanced AI ensemble strategies
- Comprehensive backtesting suite

**Best for:** Users who prefer a visual trader’s dashboard over CLI scripts.

---

## `mikhailtal-s-market-master` (Djmon007)

**Repo:** https://github.com/Djmon007/mikhailtal-s-market-master

**What it is (currently):** A modern Vite + React + Tailwind front-end template (Lovable.dev scaffold). No bot logic yet.

**Novelty vs `manifoldbot`:** Front-end-first approach instead of Python library.

**Best for:** Starting point for a custom web UI or dashboard around a Manifold bot.

---
## ContestMikhailBot (tanyat29)

**Repo:** https://github.com/barbiet503/contest-mikhail-bot

**What it is:**  
A contest-focused Python trading bot built for the Manifold Featured
Challenge, trading exclusively in markets created by **MikhailTal**.

**Novelty vs manifoldbot:**
- Strict creator-only market filtering (contest rules enforced)
- Edge + soft momentum confirmation before trading
- Risk-aware, capped position sizing
- Per-market cooldowns and duplicate-trade protection
- Clean, contest-grade logging and CSV outputs

**Best for:**  
Contest participants seeking a disciplined, explainable, and stable
Manifold trading bot rather than aggressive or overfitted strategies.

### Full list of alternatives (feel free to add more)

- https://github.com/sachin-detrax/better_manifold_bot
- https://github.com/prathameshpatrawale/ppbot-ai
- https://github.com/Sbha8282/Manifoldbot-Ultra
- https://github.com/rodriguezramirezederdominic-web/TalOS-Manifold-Bot
- https://github.com/H-tech-AFAQ-CEO/Best-Open-Source-Judgmental-Prediction-Python-Repository
- https://github.com/101jayjoshi-sudo/bot-
- https://github.com/blackXmask/Manifold-Markets-Trading-Bot
- https://github.com/Djmon007/mikhailtal-s-market-master
- https://github.com/barbiet503-bot/Strategy_contest.git

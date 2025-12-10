# Alternatives / Derivative Manifold Bots

This repository (`microprediction/manifoldbot`) is a general-purpose Python package for building Manifold trading bots, with examples such as an LLM trading bot that compares GPT-generated probabilities to market prices and bets using fractional Kelly sizing.  

Below are community-built bots that take this pattern in different directions. For each one, the focus is on **what’s novel relative to `manifoldbot`** rather than just re-implementing the same thing.

---

## `better_manifold_bot` (sachin-detrax)

**Repo:** <https://github.com/sachin-detrax/better_manifold_bot> :contentReference[oaicite:1]{index=1}  

**What it is:**  
A “souped‑up” Manifold bot using a **multi‑signal ensemble** (historical performance, market microstructure, and an OpenAI LLM) to produce a single “true probability,” plus serious tooling for performance analysis.

**Novelty vs `manifoldbot`:**

- **Multi‑signal ensemble:** Instead of relying just on an LLM or simple heuristics, it explicitly combines:
  - Historical signal (creator’s past resolution biases),
  - Microstructure signal (order book depth and recent activity),
  - OpenAI signal (structured LLM forecasting with base rates, counter‑arguments, and multiple runs). :contentReference[oaicite:2]{index=2}  
- **Variance‑aware LLM usage:** Runs the OpenAI forecast multiple times and penalizes confidence when runs disagree (“variance penalty”), reducing overconfident hallucinations. :contentReference[oaicite:3]{index=3}  
- **Ensemble decision layer:** A dedicated `EnhancedEnsembleDecisionMaker` that handles disagreement penalties and computes an “edge” from its true probability vs market probability. :contentReference[oaicite:4]{index=4}  
- **Advanced Kelly implementation:** Uses fractional Kelly (e.g. quarter‑Kelly) with caps on max bankroll fraction per trade. :contentReference[oaicite:5]{index=5}  
- **Performance tooling out of the box:** Logs detailed rationales and P&L, and generates performance graphs (cumulative P&L, win rate, etc.). :contentReference[oaicite:6]{index=6}  
- **Creator targeting:** Configurable to focus on specific creators (default: `MikhailTal`). :contentReference[oaicite:7]{index=7}  

**Best for:** People who want an “opinionated, researchy” ensemble bot with strong logging and visualization built in.

---

## `ppbot-ai` (prathameshpatrawale)

**Repo:** <https://github.com/prathameshpatrawale/ppbot-ai>   

**What it is:**  
A contest‑oriented bot built for the Manifold Featured Challenge, trading only in `MikhailTal`’s markets. It’s narrower in scope but simple and well‑structured.

**Novelty vs `manifoldbot`:**

- **Contest‑specific focus:** Hard‑wired to trade only markets by `MikhailTal`, matching the contest constraint. :contentReference[oaicite:9]{index=9}  
- **Hybrid technical strategy (no LLM required):**
  - Mean reversion (buy against extremes),
  - Momentum (follow the trend),
  - Liquidity filter (skip illiquid markets). :contentReference[oaicite:10]{index=10}  
- **Built‑in simulation toggle:** Automatically switches between real and simulation mode based on whether `MANIFOLD_API_KEY` is present. :contentReference[oaicite:11]{index=11}  
- **PnL logging + quick plotting:** Logs all trades to `pnl_log.json` and includes a script to produce a cumulative profit graph (`pnl_plot.png`). :contentReference[oaicite:12]{index=12}  
- **Clean modular layout:** Separate modules for strategy, client, simulation, and PnL, but with less framework overhead than `manifoldbot` itself. :contentReference[oaicite:13]{index=13}  

**Best for:** A compact reference implementation of a non‑LLM strategy bot targeting one creator, with minimal ceremony and simple PnL analysis.

---

## `Manifoldbot-Ultra` (Sbha8282)

**Repo:** <https://github.com/Sbha8282/Manifoldbot-Ultra>  

**What it is:**  
A **packaged, modular bot** designed as a clean Python package (`manifold_ultra_bot`) with dry‑run by default and optional LLM‑backed probabilities.

**Novelty vs `manifoldbot`:**

- **Modern package layout:** Built as a Python 3.10+ package with a clearly separated `src/` structure and tests, whereas `manifoldbot` is both a package and an examples repo. :contentReference[oaicite:15]{index=15}  
- **Strict creator targeting:** Environment variable `TARGET_CREATOR` to focus on a single creator (again usually `MikhailTal`). :contentReference[oaicite:16]{index=16}  
- **Session‑cookie based betting:** Uses a `MANIFOLD_SESSION_COOKIE` to place bets, rather than only the API key, which can be more convenient for some workflows. :contentReference[oaicite:17]{index=17}  
- **Default to safe simulation:** `DRY_RUN=true` by default so you don’t accidentally place live bets. :contentReference[oaicite:18]{index=18}  
- **Optional LLM probability layer:** Heuristic estimate by default; if `OPENAI_API_KEY` is set, it can ask an LLM for calibrated probabilities. :contentReference[oaicite:19]{index=19}  

**Best for:** People who want a slightly more “production‑ready” package skeleton, with clear separation between fetching, strategy, and execution.

---

## `TalOS-Manifold-Bot` (rodriguezramirezederdominic-web)

**Repo:** <https://github.com/rodriguezramirezederdominic-web/TalOS-Manifold-Bot>  

**What it is:**  
A self‑described **agentic** bot (TalOS) that uses GPT‑4 to read market text, perform reference‑class reasoning, and then bet using Fractional Kelly, targeted at `MikhailTal` markets.

**Novelty vs `manifoldbot`:**

- **Agentic LLM design:** Instead of simple prompt+probability, TalOS uses an LLM (GPT‑4) to “read the market,” perform reference‑class analysis, and then emit a calibrated probability. :contentReference[oaicite:21]{index=21}  
- **Fractional Kelly money management:** Explicit Fractional Kelly implementation to size bets based on perceived edge, emphasizing risk‑of‑ruin reduction. :contentReference[oaicite:22]{index=22}  
- **Clear modular separation:**
  - `TalOs_bot.py` – trading loop,
  - `brain.py` – decision/LLM logic,
  - `kelly.py` – bankroll math. :contentReference[oaicite:23]{index=23}  
- **Single‑creator focus:** API filtering to target a specific creator ID. :contentReference[oaicite:24]{index=24}  

**Best for:** People interested in a very readable “LLM brain + Kelly sizing” example with strong emphasis on agentic reasoning.

---

## `Best-Open-Source-Judgmental-Prediction-Python-Repository` (“Afaq”)

**Repo:** <https://github.com/H-tech-AFAQ-CEO/Best-Open-Source-Judgmental-Prediction-Python-Repository>   

**What it is:**  
Despite the long name, the README describes a **Manifold Markets Trading Bot**: a clean modular Python bot focusing on `MikhailTal` markets with both simple and LLM strategies.

**Novelty vs `manifoldbot`:**

- **Emphasis on code quality:** Advertises cleaner architecture, **full type hints**, and better error handling with logging. :contentReference[oaicite:26]{index=26}  
- **Modular strategy system:** Uses a base strategy class with both `SimpleStrategy` (threshold rules) and `LLMStrategy` (OpenAI‑based fair‑value estimation). :contentReference[oaicite:27]{index=27}  
- **Integrated backtesting:** Ships with `backtest.py` and an explicit backtesting mode mentioned in both the Features and Improvements section. :contentReference[oaicite:28]{index=28}  
- **Risk management / cooldowns:** Includes risk controls and cooldown mechanisms beyond the raw examples in `manifoldbot`. :contentReference[oaicite:29]{index=29}  
- **PR‑ready positioning:** README explicitly says it’s designed to be “PR-ready” for `microprediction/manifoldbot` with these improvements. :contentReference[oaicite:30]{index=30}  

**Best for:** Using as a “polished, typed, backtestable” variant if you care about code hygiene and want an easy base for PRs upstream.

---

## `bot-` (“Joshi-Bot”, 101jayjoshi-sudo)

**Repo:** <https://github.com/101jayjoshi-sudo/bot->  

**What it is:**  
A **lightweight `tal-manifold-bot` scaffold** that trades only `MikhailTal` markets using heuristics and optional local model hooks.

**Novelty vs `manifoldbot`:**

- **Very lightweight scaffold:** Minimal repo whose goal is to provide “clean repo structure and easy instructions to push to GitHub,” rather than a full library. :contentReference[oaicite:32]{index=32}  
- **Heuristics + optional local model:** Uses an ensemble of heuristics in `strategy.py` with optional hooks for a local model, instead of being tightly coupled to OpenAI APIs. :contentReference[oaicite:33]{index=33}  
- **Dry‑run first:** Bets are disabled by default; you must explicitly set `PLACE_BETS=true` to enable real trades. :contentReference[oaicite:34]{index=34}  
- **Creator‑resolution workflow:** Explicitly resolves the `MikhailTal` username to a user ID via the Manifold API, then fetches markets by that creator. :contentReference[oaicite:35]{index=35}  

**Best for:** A tiny, hackable bot template where you want to plug in your own heuristics or local models without a lot of framework.

---

## `Manifold-Markets-Trading-Bot` (blackXmask)

**Repo:** <https://github.com/blackXmask/Manifold-Markets-Trading-Bot>  

**What it is:**  
A **full trading “app”** for Manifold, not just a script: Streamlit GUI, portfolio analytics, arbitrage detection, and advanced AI strategies, again focused on `MikhailTal` markets.

**Novelty vs `manifoldbot`:**

- **Large GUI surface area:** Streamlit app with a dark‑theme, multiple interactive tabs, live market monitoring, P&L, ROI, win rate, correlation heatmaps, etc. :contentReference[oaicite:37]{index=37}  
- **Portfolio‑level thinking:** Has portfolio optimization (correlation, diversification, position sizing) and portfolio/P&L tracking, not just independent trade decisions. :contentReference[oaicite:38]{index=38}  
- **Arbitrage engine:** Explicit arbitrage detection for binary and cross‑market opportunities. :contentReference[oaicite:39]{index=39}  
- **Ensemble AI strategies:** Mentions GPT‑5 probability estimation, sentiment analysis, and ensemble learning as part of strategy definition. :contentReference[oaicite:40]{index=40}  
- **Backtesting built in:** Historical simulations and strategy comparisons are first‑class features. :contentReference[oaicite:41]{index=41}  

**Best for:** Someone who wants a “trader’s dashboard” with buttons and charts, rather than a pure Python CLI/package.

---

## `mikhailtal-s-market-master` (“dwashil”, Djmon007)

**Repo:** <https://github.com/Djmon007/mikhailtal-s-market-master>  

**What it is (currently):**  
At the time of writing, this repo appears to be a **Lovable.dev web app scaffold**: a Vite + TypeScript + React + Tailwind + shadcn‑ui front‑end template, with a README describing how to edit and deploy via Lovable. There is no documented bot logic or Manifold‑specific description yet. :contentReference[oaicite:43]{index=43}  

**Novelty vs `manifoldbot`:**

- **Front‑end–first approach:** Unlike `manifoldbot` (which is a Python library), this is a TypeScript/React front‑end template that could become a UI for a bot or dashboard. :contentReference[oaicite:44]{index=44}  
- **Lovable integration:** The README is auto‑generated for Lovable, emphasizing edit‑via‑prompt and one‑click deploy flows; the “novelty” here is more about development environment than trading logic. :contentReference[oaicite:45]{index=45}  

**Caveat:** As of now, there’s no clear description of how it interacts with Manifold or any novel strategy. It may evolve into a visual interface or manager for a bot, but that’s not documented yet.

**Best for:** A starting point if you want to build a custom web UI around a Manifold bot using modern TS/React tooling.

---

### Full list of alternatives

Some other packages that improve on this one (maybe). Please star them if you like them. 


- [better_manifold_bot](https://github.com/sachin-detrax/better_manifold_bot)
- [ppbot-ai](https://github.com/prathameshpatrawale/ppbot-ai)
- [manifold-ultra](https://github.com/Sbha8282/Manifoldbot-Ultra)
- [TalOS-Manifold-Bot](https://github.com/rodriguezramirezederdominic-web/TalOS-Manifold-Bot)
- [Afaq](https://github.com/H-tech-AFAQ-CEO/Best-Open-Source-Judgmental-Prediction-Python-Repository)
- [Joshi-Bot](https://github.com/101jayjoshi-sudo/bot-)
- [blackxmask](https://github.com/blackXmask/Manifold-Markets-Trading-Bot)
- [dwashil](https://github.com/Djmon007/mikhailtal-s-market-master)

# Intelligent Broker Desk

A Streamlit-based AI broker desk that turns a plain English trading instruction into market analysis, news sentiment, strategy scoring, risk review and optional Alpaca paper trading.

Live app: https://ai-broker-desk.streamlit.app/

## Overview

Intelligent Broker Desk demonstrates how a broker-style workflow can move from research to controlled execution.

The app does not place an order just because the user asks for one. It first checks market conditions, reviews recent news, scores the strategy, applies risk controls and then decides whether the trade should be analysed, simulated, routed as a paper order or blocked.

This project is built for demos, education and paper trading only.

## How it works

Example instruction:

```text
Buy 1 AAPL at market
```

The app extracts:

```text
Ticker: AAPL
Side: BUY
Quantity: 1
```

The request then moves through the agent pipeline:

```text
User Instruction
→ Broker Orchestrator
→ Market Agent
→ News Agent
→ Strategy Agent
→ Risk Agent
→ Execution Agent
→ Final Decision + Audit Trail
```

## Agents

### Market Agent

Uses `yfinance` to review recent price history.

It checks:

* Latest price
* Daily price change
* 20-day moving average
* 50-day moving average

Market scoring:

| Condition                     | Trend   | Score |
| ----------------------------- | ------- | ----: |
| Price > 20-day MA > 50-day MA | Bullish |    80 |
| Price < 20-day MA < 50-day MA | Bearish |    30 |
| Mixed price action            | Neutral |    55 |

### News Agent

Reads up to five recent headlines from `yfinance` and scores headline tone.

The score starts at `50`.

Positive words such as `growth`, `upgrade`, `strong`, `profit`, `rally` and `outperform` increase the score.

Negative words such as `miss`, `drop`, `downgrade`, `loss`, `lawsuit`, `probe` and `warning` reduce the score.

| Score | Sentiment |
| ----: | --------- |
|   65+ | Positive  |
| 41–64 | Neutral   |
|  0–40 | Negative  |

If no headlines are found, sentiment defaults to Neutral.

### Strategy Agent

Combines market trend, news sentiment and volatility into one confidence score.

| Factor                  | Weight |
| ----------------------- | -----: |
| Market trend            |    50% |
| News sentiment          |    35% |
| Volatility / daily move |    15% |

```text
Strategy Confidence =
Market Trend Score × 50%
+ News Sentiment Score × 35%
+ Volatility Score × 15%
```

Volatility scoring:

| Daily move | Status     | Score |
| ---------: | ---------- | ----: |
|   Up to 2% | Acceptable |    80 |
|   2% to 5% | Elevated   |    55 |
|   Above 5% | High       |    30 |

Strategy signals:

| Signal | Meaning                                                                           |
| ------ | --------------------------------------------------------------------------------- |
| BUY    | Confidence is at least 65, trend is Bullish, and sentiment is Positive or Neutral |
| AVOID  | Confidence is 40 or below, trend is Bearish, or sentiment is Negative             |
| HOLD   | Setup is not strong enough for Buy, but not weak enough for Avoid                 |

A Buy signal does not automatically place an order. It still needs to pass the Risk Agent.

### Risk Agent

The Risk Agent checks whether the trade is acceptable before execution.

It reviews:

* Valid ticker price
* Valid BUY or SELL side
* Valid quantity
* Strategy confidence
* Order size
* Daily movement
* Volatility
* Demo exposure limit

Current risk rules:

| Rule                             |     Value |
| -------------------------------- | --------: |
| Maximum paper notional           |    $5,000 |
| Clean-trade confidence threshold |       60% |
| Small paper ticket limit         |    $1,000 |
| Extreme daily move block         | Above 12% |

Risk levels:

| Condition                                     | Risk level | Score |
| --------------------------------------------- | ---------- | ----: |
| Up to $1,000 notional and up to 2% daily move | Low        |    25 |
| Up to $5,000 notional and up to 5% daily move | Medium     |    55 |
| Larger or more volatile tickets               | High       |    80 |

If the requested quantity is too large, the Risk Agent can reduce the approved quantity to stay within the `$5,000` demo notional limit.

It also shows a reference stop-loss:

* BUY: around 3% below latest price
* SELL: around 3% above latest price

### Execution Agent

The Execution Agent only runs when the Risk Agent approves the ticket.

It can:

* Stop the order in Analysis Only mode
* Create a simulated demo order
* Submit a paper market order to Alpaca

It blocks execution if risk approval is missing, the side is not BUY or SELL, approved quantity is zero, Alpaca credentials are missing, or the execution mode is not valid.

## Execution modes

### Analysis Only

Runs the full pipeline but does not place any order.

Best for research, testing and safe demos.

### Demo Execution

Runs the full pipeline and creates a simulated demo order ID when approved.

No Alpaca order is placed.

### Alpaca Paper Trading

Routes approved orders to the user’s own Alpaca paper trading account.

This uses simulated paper money, not live capital. Users must enter their own Alpaca Paper API key and secret before routing is enabled.

Alpaca paper orders use:

* Market order
* Day time-in-force
* User-provided paper credentials
* Paper trading account only

## When the app may buy

The app may approve a paper buy when:

* The user clearly asks to buy
* The ticker is recognised
* Quantity is valid
* Market data is available
* Strategy confidence is strong enough, or the ticket is small enough to pass with caution
* Daily movement is not extreme
* Risk controls approve the ticket
* The selected execution mode allows routing

Small paper trades can pass with caution because this is a controlled demo environment.

## When the app blocks a trade

The app can block or avoid a trade when:

* Market data is unavailable
* Side or quantity is unclear
* Strategy confidence is too low for the order size
* Trend is bearish
* News sentiment is negative
* Volatility is high for a larger ticket
* Daily move is above 12%
* Alpaca paper credentials are missing
* The app is in Analysis Only mode

This is intentional. The system is designed to explain why a trade was approved, blocked or kept as analysis only.

## Supported demo inputs

The app supports common company names and tickers such as:

* Apple / AAPL
* Nvidia / NVDA
* Tesla / TSLA
* Microsoft / MSFT
* Amazon / AMZN
* Google / GOOGL
* Meta / META

Uppercase ticker symbols can also be detected directly.

## Tech stack

* Python
* Streamlit
* yfinance
* Alpaca Paper Trading API
* SQLite run history
* Multi-agent workflow
* GitHub
* Streamlit Cloud

## Future improvements

Possible next steps:

* More tickers and asset classes
* Portfolio and position tracking
* Market open / close awareness
* Backtesting
* Trade history analytics
* Stronger risk rules
* Better news sentiment scoring
* User accounts and saved watchlists
* More advanced order types
* Broker-grade compliance controls

## Important note

This project is for education, demos and paper trading only. It is not financial advice and should not be used for live trading without proper compliance, risk management and regulatory review.

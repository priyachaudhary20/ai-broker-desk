import yfinance as yf


def run_market_agent(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="3mo")

        if hist.empty:
            return {
                "agent": "Market Agent",
                "status": "failed",
                "summary": f"No market data found for {ticker}.",
                "data": {}
            }

        latest_price = float(hist["Close"].iloc[-1])
        previous_price = float(hist["Close"].iloc[-2])

        daily_change_pct = ((latest_price - previous_price) / previous_price) * 100

        hist["MA20"] = hist["Close"].rolling(window=20).mean()
        hist["MA50"] = hist["Close"].rolling(window=50).mean()

        ma20 = float(hist["MA20"].iloc[-1])
        ma50 = float(hist["MA50"].iloc[-1])

        if latest_price > ma20 > ma50:
            trend = "Bullish"
            trend_score = 80
        elif latest_price < ma20 < ma50:
            trend = "Bearish"
            trend_score = 30
        else:
            trend = "Neutral"
            trend_score = 55

        return {
            "agent": "Market Agent",
            "status": "complete",
            "summary": f"{ticker} is currently {trend}. Latest price: ${latest_price:.2f}.",
            "data": {
                "ticker": ticker,
                "latest_price": round(latest_price, 2),
                "daily_change_pct": round(daily_change_pct, 2),
                "ma20": round(ma20, 2),
                "ma50": round(ma50, 2),
                "trend": trend,
                "trend_score": trend_score
            }
        }

    except Exception as e:
        return {
            "agent": "Market Agent",
            "status": "error",
            "summary": f"Market Agent failed: {str(e)}",
            "data": {}
        }
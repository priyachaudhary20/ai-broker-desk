BUY_CONFIDENCE_THRESHOLD = 65
AVOID_CONFIDENCE_THRESHOLD = 40

def run_strategy_agent(market_data: dict, news_data: dict) -> dict:
    """
    Strategy Agent decides whether conditions suggest BUY, HOLD, or AVOID.

    This is rule-based for demo clarity:
    - Market trend contributes 50%
    - News sentiment contributes 35%
    - Volatility/daily movement contributes 15%
    """

    try:
        ticker = market_data.get("ticker", "UNKNOWN")

        trend = market_data.get("trend", "Neutral")
        trend_score = market_data.get("trend_score", 50)

        sentiment = news_data.get("sentiment", "Neutral")
        sentiment_score = news_data.get("sentiment_score", 50)

        daily_change_pct = market_data.get("daily_change_pct", 0)
        abs_daily_change = abs(daily_change_pct)

        # Volatility score: lower daily movement is safer for entry
        if abs_daily_change <= 2:
            volatility_score = 80
            volatility_status = "Acceptable"
        elif abs_daily_change <= 5:
            volatility_score = 55
            volatility_status = "Elevated"
        else:
            volatility_score = 30
            volatility_status = "High"

        confidence = int(
            (trend_score * 0.50)
            + (sentiment_score * 0.35)
            + (volatility_score * 0.15)
        )

        if (
            confidence >= BUY_CONFIDENCE_THRESHOLD
            and trend == "Bullish"
            and sentiment in ["Positive", "Neutral"]
        ):
            signal = "BUY"
        elif (
            confidence <= AVOID_CONFIDENCE_THRESHOLD
            or trend == "Bearish"
            or sentiment == "Negative"
        ):
            signal = "AVOID"
        else:
            signal = "HOLD"

        reasons = []

        if trend == "Bullish":
            reasons.append("Market trend is bullish, supporting a possible entry")
        elif trend == "Bearish":
            reasons.append("Market trend is bearish, so entry should be avoided")
        else:
            reasons.append("Market trend is neutral, so there is no strong trend confirmation")

        if sentiment == "Positive":
            reasons.append("News sentiment is positive, supporting confidence")
        elif sentiment == "Negative":
            reasons.append("News sentiment is negative, reducing confidence")
        else:
            reasons.append("News sentiment is neutral, so there is no strong news catalyst")

        if volatility_status == "Acceptable":
            reasons.append("Daily movement is acceptable for entry")
        elif volatility_status == "Elevated":
            reasons.append("Daily movement is elevated, so entry is not ideal yet")
        else:
            reasons.append("Daily movement is high, so trade should be avoided")

        reason_text = ". ".join(reasons) + "."

        return {
            "agent": "Strategy Agent",
            "status": "complete",
            "summary": f"{ticker} strategy signal is {signal} with {confidence}% confidence. Buy threshold: {BUY_CONFIDENCE_THRESHOLD}%.",
            "data": {
                "ticker": ticker,
                "signal": signal,
                "confidence": confidence,
                "trend": trend,
                "trend_score": trend_score,
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "daily_change_pct": daily_change_pct,
                "volatility_status": volatility_status,
                "volatility_score": volatility_score,
                "reason": reason_text,
            },
        }

    except Exception as e:
        return {
            "agent": "Strategy Agent",
            "status": "error",
            "summary": f"Strategy Agent failed: {str(e)}",
            "data": {
                "signal": "HOLD",
                "confidence": 50,
                "reason": "Strategy failed, defaulting to HOLD.",
            },
        }
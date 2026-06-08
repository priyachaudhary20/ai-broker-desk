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
            reasons.append("Market structure is bullish, with price action supporting a potential long-side entry")
        elif trend == "Bearish":
            reasons.append("Market structure is bearish, so the desk should avoid initiating a long-side order")
        else:
            reasons.append("Market structure is neutral, with no clear directional confirmation from the moving-average setup")

        if sentiment == "Positive":
            reasons.append("Headline tone is positive, adding support to the strategy conviction")
        elif sentiment == "Negative":
            reasons.append("Headline tone is negative, reducing strategy conviction")
        else:
            reasons.append("Headline tone is neutral, with no clear news-driven catalyst identified")

        if volatility_status == "Acceptable":
            reasons.append("Short-term price movement is within acceptable range for a paper-trading entry")
        elif volatility_status == "Elevated":
            reasons.append("Short-term price movement is elevated, so entry conditions are not ideal yet")
        else:
            reasons.append("Short-term price movement is high, so the setup should be avoided under current desk rules")

        reason_text = ". ".join(reasons) + "."

        return {
            "agent": "Strategy Agent",
            "status": "complete",
            "summary": f"Strategy Agent assigns {ticker} a {signal} signal with {confidence}/100 conviction. Buy threshold: {BUY_CONFIDENCE_THRESHOLD}/100.",
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
            "summary": f"Strategy Agent could not complete signal generation: {str(e)}",
            "data": {
                "signal": "HOLD",
                "confidence": 50,
                "reason": "Strategy signal generation could not be completed. The desk defaults to HOLD for safety.",
            },
        }
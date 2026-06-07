MAX_DEMO_NOTIONAL = 5000
MIN_CONFIDENCE_FOR_TRADE = 60


def run_risk_agent(
    market_data: dict,
    strategy_data: dict,
    requested_quantity: int,
    side: str
) -> dict:
    """
    Risk Agent checks whether a proposed trade is acceptable.

    It controls:
    - Maximum notional exposure.
    - Position sizing.
    - Stop-loss level.
    - Strategy confidence.
    - Volatility conditions.
    - Trade approval or blocking.
    """

    try:
        ticker = market_data.get("ticker", "UNKNOWN")
        latest_price = market_data.get("latest_price", 0)
        daily_change_pct = market_data.get("daily_change_pct", 0)

        signal = strategy_data.get("signal", "HOLD")
        confidence = strategy_data.get("confidence", 50)
        volatility_status = strategy_data.get("volatility_status", "Unknown")

        if latest_price <= 0:
            return {
                "agent": "Risk Agent",
                "status": "blocked",
                "summary": "Risk Agent blocked the trade because price data is unavailable.",
                "data": {
                    "approval": "Blocked",
                    "risk_level": "High",
                    "reason": "Price data is unavailable.",
                },
            }

        max_quantity_allowed = int(MAX_DEMO_NOTIONAL // latest_price)

        if max_quantity_allowed < 1:
            max_quantity_allowed = 1

        approved_quantity = min(requested_quantity, max_quantity_allowed)
        notional = approved_quantity * latest_price

        abs_daily_change = abs(daily_change_pct)

        if notional <= 1000 and abs_daily_change <= 2:
            risk_level = "Low"
            risk_score = 80
        elif notional <= 5000 and abs_daily_change <= 5:
            risk_level = "Medium"
            risk_score = 60
        else:
            risk_level = "High"
            risk_score = 30

        stop_loss = None

        if side == "BUY":
            stop_loss = latest_price * 0.97
        elif side == "SELL":
            stop_loss = latest_price * 1.03

        approval = "Approved"
        reasons = []

        if side == "ANALYSE":
            approval = "Blocked"
            reasons.append(
                "No trade direction was detected. This request has been treated as analysis only."
            )

        if signal != "BUY":
            approval = "Blocked"
            reasons.append(
                f"The strategy signal is {signal}. Execution is not recommended."
            )

        if confidence < MIN_CONFIDENCE_FOR_TRADE:
            approval = "Blocked"
            reasons.append(
                f"Strategy confidence is below the required {MIN_CONFIDENCE_FOR_TRADE}% threshold."
            )

        if volatility_status == "High":
            approval = "Blocked"
            reasons.append(
                "Market volatility is high. The trade has been blocked for risk control."
            )

        if approval == "Approved":
            reasons.append("The trade passes demo risk checks.")

        if requested_quantity > approved_quantity:
            reasons.append(
                f"The requested quantity was reduced from {requested_quantity} to {approved_quantity} to stay within the demo risk limit."
                )

        if approval == "Approved" and requested_quantity > approved_quantity:
            approval = "Approved with Adjustment"

        if risk_level == "High":
            approval = "Blocked"
            reasons.append(
                "The risk level is high. The trade has been blocked."
            )

        if not reasons:
            reasons.append(
                "The proposed trade passes all demo risk checks."
            )

        reason_text = " ".join(reasons)

        return {
            "agent": "Risk Agent",
            "status": "complete",
            "summary": f"{ticker} risk status: {approval}. Risk level: {risk_level}.",
            "data": {
                "ticker": ticker,
                "side": side,
                "approval": approval,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "requested_quantity": requested_quantity,
                "approved_quantity": approved_quantity,
                "latest_price": round(latest_price, 2),
                "notional": round(notional, 2),
                "stop_loss": round(stop_loss, 2) if stop_loss else None,
                "max_demo_notional": MAX_DEMO_NOTIONAL,
                "strategy_signal": signal,
                "strategy_confidence": confidence,
                "volatility_status": volatility_status,
                "reason": reason_text,
            },
        }

    except Exception as e:
        return {
            "agent": "Risk Agent",
            "status": "error",
            "summary": f"Risk Agent failed: {str(e)}",
            "data": {
                "approval": "Blocked",
                "risk_level": "High",
                "reason": "Risk assessment failed. The trade has been blocked by default.",
            },
        }
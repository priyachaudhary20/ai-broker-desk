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
    - Stop-loss reference level.
    - Strategy confidence.
    - Volatility conditions.
    - Trade approval or blocking.

    This version is demo-safe but not overly restrictive:
    - BUY 1 AAPL should pass if price data is valid.
    - Small paper trades can pass with caution.
    - Large or invalid trades are still blocked or resized.
    """

    try:
        ticker = market_data.get("ticker", "UNKNOWN")
        latest_price = float(market_data.get("latest_price", 0) or 0)
        daily_change_pct = float(market_data.get("daily_change_pct", 0) or 0)

        signal = str(strategy_data.get("signal", "HOLD")).upper()
        confidence = int(strategy_data.get("confidence", 50) or 50)
        volatility_status = str(strategy_data.get("volatility_status", "Unknown"))

        side = str(side or "").upper()

        try:
            requested_quantity = int(requested_quantity)
        except Exception:
            requested_quantity = 0

        if latest_price <= 0:
            return {
                "agent": "Risk Agent",
                "status": "blocked",
                "summary": "Risk Agent held the ticket because valid price data was unavailable for pre-trade review.",
                "data": {
                    "ticker": ticker,
                    "side": side,
                    "approval": "Blocked",
                    "risk_level": "High",
                    "risk_score": 90,
                    "requested_quantity": requested_quantity,
                    "approved_quantity": 0,
                    "latest_price": 0,
                    "notional": 0,
                    "stop_loss": None,
                    "max_demo_notional": MAX_DEMO_NOTIONAL,
                    "strategy_signal": signal,
                    "strategy_confidence": confidence,
                    "volatility_status": volatility_status,
                    "reason": "No valid latest price was available, so the order cannot be assessed against notional and risk limits.",
                },
            }

        if side not in ["BUY", "SELL"]:
            return {
                "agent": "Risk Agent",
                "status": "complete",
                "summary": "Risk Agent treated this request as analysis-only because no executable BUY or SELL side was detected.",
                "data": {
                    "ticker": ticker,
                    "side": side,
                    "approval": "Blocked",
                    "risk_level": "Low",
                    "risk_score": 20,
                    "requested_quantity": requested_quantity,
                    "approved_quantity": 0,
                    "latest_price": round(latest_price, 2),
                    "notional": 0,
                    "stop_loss": None,
                    "max_demo_notional": MAX_DEMO_NOTIONAL,
                    "strategy_signal": signal,
                    "strategy_confidence": confidence,
                    "volatility_status": volatility_status,
                    "reason": "No executable side was detected. The instruction has been treated as an analysis-only request.",
                },
            }

        if requested_quantity <= 0:
            return {
                "agent": "Risk Agent",
                "status": "complete",
                "summary": "Risk Agent blocked the ticket because the requested quantity was missing or invalid.",
                "data": {
                    "ticker": ticker,
                    "side": side,
                    "approval": "Blocked",
                    "risk_level": "High",
                    "risk_score": 90,
                    "requested_quantity": requested_quantity,
                    "approved_quantity": 0,
                    "latest_price": round(latest_price, 2),
                    "notional": 0,
                    "stop_loss": None,
                    "max_demo_notional": MAX_DEMO_NOTIONAL,
                    "strategy_signal": signal,
                    "strategy_confidence": confidence,
                    "volatility_status": volatility_status,
                    "reason": "Requested quantity was missing, zero or negative.",
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
            risk_score = 25
        elif notional <= MAX_DEMO_NOTIONAL and abs_daily_change <= 5:
            risk_level = "Medium"
            risk_score = 55
        else:
            risk_level = "High"
            risk_score = 80

        stop_loss = None

        if side == "BUY":
            stop_loss = latest_price * 0.97
        elif side == "SELL":
            stop_loss = latest_price * 1.03

        approval = "Approved"
        reasons = []

        if requested_quantity > approved_quantity:
            reasons.append(
                f"Order size was adjusted from {requested_quantity} to {approved_quantity} share(s) to remain within the ${MAX_DEMO_NOTIONAL} paper notional limit."
            )

        # Strategy alignment checks
        if side == "BUY" and signal in ["BUY", "STRONG_BUY"]:
            reasons.append("Strategy signal is aligned with the requested BUY order.")

        elif side == "SELL" and signal in ["SELL", "STRONG_SELL", "AVOID"]:
            reasons.append("Strategy signal is aligned with the requested SELL order.")

        elif signal == "HOLD":
            reasons.append(
                "Strategy signal is HOLD. The ticket is approved for paper trading with caution because the order size is within limits."
            )

        else:
            reasons.append(
                f"Strategy signal is {signal}, which is not fully aligned with the requested {side} order. The ticket is approved for paper trading with caution."
            )

        # Confidence check
        if confidence < MIN_CONFIDENCE_FOR_TRADE:
            if notional <= 1000:
                reasons.append(
                    f"Strategy confidence is {confidence}%, below the clean-trade threshold of {MIN_CONFIDENCE_FOR_TRADE}%, but the ticket is small and approved for paper trading with caution."
                )
            else:
                approval = "Blocked"
                reasons.append(
                    f"Strategy confidence is {confidence}%, below the required {MIN_CONFIDENCE_FOR_TRADE}% threshold for this order size."
                )

        # Volatility check
        if volatility_status == "High":
            if notional <= 1000:
                reasons.append(
                    "Market volatility is high, but the ticket is small and approved for paper trading with caution."
                )
            else:
                approval = "Blocked"
                reasons.append(
                    "Market volatility is high. Larger tickets are blocked by pre-trade risk controls."
                )

        # Extreme daily move check
        if abs_daily_change > 12:
            approval = "Blocked"
            reasons.append(
                "The daily move is above 12%, which is outside the allowed paper-trading risk envelope."
            )

        # High risk check
        if risk_level == "High" and notional > 1000:
            approval = "Blocked"
            reasons.append(
                "Overall risk level is High for this order size. The ticket has been blocked before execution."
            )

        if approved_quantity <= 0:
            approval = "Blocked"
            reasons.append("Approved quantity is zero after risk sizing.")

        if not reasons:
            reasons.append("The proposed ticket passes all configured pre-trade risk checks.")

        if approval == "Blocked":
            final_approved_quantity = 0
            final_notional = 0
        else:
            final_approved_quantity = approved_quantity
            final_notional = notional

        reason_text = " ".join(reasons)

        return {
            "agent": "Risk Agent",
            "status": "complete",
            "summary": (
                f"Risk Agent review for {ticker}: {approval}. "
                f"Risk level: {risk_level}; approved size: {final_approved_quantity} share(s); "
                f"estimated notional: ${final_notional:.2f}."
            ),
            "data": {
                "ticker": ticker,
                "side": side,
                "approval": approval,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "requested_quantity": requested_quantity,
                "approved_quantity": final_approved_quantity,
                "latest_price": round(latest_price, 2),
                "notional": round(final_notional, 2),
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
            "summary": f"Risk Agent could not complete the pre-trade review: {str(e)}",
            "data": {
                "approval": "Blocked",
                "risk_level": "High",
                "risk_score": 100,
                "reason": "Pre-trade risk assessment could not be completed. The ticket has been blocked by default.",
            },
        }
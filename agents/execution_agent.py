from datetime import datetime, timezone
import uuid

from brokers.alpaca_client import submit_paper_market_order

def run_execution_agent(risk_result: dict, execution_mode: str = "Analysis Only", alpaca_credentials: dict | None = None,) -> dict:
    """
    Execution Agent submits an approved paper trade to Alpaca.

    It only runs when the Risk Agent approval starts with 'Approved'.
    """

    try:
        risk_data = risk_result.get("data", risk_result)
        approval = risk_data.get("approval", "Blocked")
        ticker = risk_data.get("ticker", "UNKNOWN")
        side = risk_data.get("side", "ANALYSE")
        approved_quantity = int(risk_data.get("approved_quantity", 0))

        if not approval.startswith("Approved"):
            return {
                "agent": "Execution Agent",
                "status": "blocked",
                "summary": "Execution Agent held the order because pre-trade risk approval was not granted.",
                "data": {
                    "execution_mode": execution_mode,
                    "order_status": "Blocked",
                    "reason": "Pre-trade risk approval is required before execution.",
                },
            }

        if side not in ["BUY", "SELL"]:
            return {
                "agent": "Execution Agent",
                "status": "blocked",
                "summary": "Execution Agent held the order because no executable BUY or SELL side was provided.",
                "data": {
                    "execution_mode": execution_mode,
                    "order_status": "Blocked",
                    "reason": "The order requires a valid BUY or SELL side before it can be routed.",
                },
            }

        if approved_quantity <= 0:
            return {
                "agent": "Execution Agent",
                "status": "blocked",
                "summary": "Execution Agent held the order because the approved quantity was zero.",
                "data": {
                    "execution_mode": execution_mode,
                    "order_status": "Blocked",
                    "reason": "Approved quantity must be greater than zero before the order can be submitted.",
                },
            }

        if execution_mode == "Analysis Only":
            return {
                "agent": "Execution Agent",
                "status": "not_routed",
                "summary": "Execution Agent did not route an order because Analysis Only mode is active.",
                "data": {
                    "execution_mode": "Analysis Only",
                    "order_status": "Not Routed",
                    "ticker": ticker,
                    "side": side,
                    "quantity": approved_quantity,
                    "reason": "Analysis Only mode prevents order submission.",
                },
            }

        if execution_mode == "Demo Execution":
            demo_order_id = f"DEMO-{uuid.uuid4()}"

            return {
                "agent": "Execution Agent",
                "status": "simulated",
                "summary": f"Execution Agent simulated a {side} demo order for {approved_quantity} share(s) of {ticker}.",
                "data": {
                    "execution_mode": "Demo Execution",
                    "order_status": "Simulated",
                    "order_id": demo_order_id,
                    "ticker": ticker,
                    "side": side,
                    "quantity": approved_quantity,
                    "order_type": "market",
                    "time_in_force": "day",
                    "submitted_at": datetime.now(timezone.utc).isoformat(),
                    "simulated": True,
                    "reason": "Demo Execution mode does not send orders to Alpaca.",
                },
            }

        if execution_mode == "Alpaca Paper Trading" and not alpaca_credentials:
            return {
                "agent": "Execution Agent",
                "status": "blocked",
                "summary": "Execution Agent blocked Alpaca routing because paper credentials were not provided.",
                "data": {
                    "execution_mode": "Alpaca Paper Trading",
                "order_status": "Blocked",
                "ticker": ticker,
                "side": side,
                "quantity": approved_quantity,
                "reason": "Enter Alpaca Paper API credentials before routing an order.",
            },
        }

        if execution_mode != "Alpaca Paper Trading":
            return {
                "agent": "Execution Agent",
                "status": "blocked",
                "summary": "Execution Agent blocked the order because the selected execution mode is not recognised.",
                "data": {
                    "execution_mode": execution_mode,
                    "order_status": "Blocked",
                    "ticker": ticker,
                    "side": side,
                    "quantity": approved_quantity,
                    "reason": "Unknown execution mode.",
                },
            }
        
        order = submit_paper_market_order(
            symbol=ticker,
            qty=approved_quantity,
            side=side,
            alpaca_credentials=alpaca_credentials,
        )


        return {
            "agent": "Execution Agent",
            "status": "complete",
            "summary": f"Execution Agent routed a {side} paper market order for {approved_quantity} share(s) of {ticker} to Alpaca.",
            "data": {
                "execution_mode": execution_mode,
                "order_status": order.get("status"),
                "order_id": order.get("order_id"),
                "client_order_id": order.get("client_order_id"),
                "ticker": order.get("symbol"),
                "side": order.get("side"),
                "quantity": order.get("qty"),
                "order_type": order.get("order_type"),
                "time_in_force": order.get("time_in_force"),
                "submitted_at": order.get("submitted_at"),
            },
        }

    except Exception as e:
        return {
            "agent": "Execution Agent",
            "status": "error",
            "summary": f"Execution Agent could not complete paper order routing: {str(e)}",
            "data": {
                "execution_mode": execution_mode,
                "order_status": "Error",
                "reason": f"Alpaca paper order routing failed before confirmation: {str(e)}",
            },
        }
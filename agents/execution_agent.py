from brokers.alpaca_client import submit_paper_market_order

def run_execution_agent(risk_data: dict) -> dict:
    """
    Execution Agent submits an approved paper trade to Alpaca.

    It only runs when the Risk Agent approval starts with 'Approved'.
    """

    try:
        approval = risk_data.get("approval", "Blocked")
        ticker = risk_data.get("ticker", "UNKNOWN")
        side = risk_data.get("side", "ANALYSE")
        approved_quantity = int(risk_data.get("approved_quantity", 0))

        if not approval.startswith("Approved"):
            return {
                "agent": "Execution Agent",
                "status": "blocked",
                "summary": "Execution Agent blocked the order because risk approval was not granted.",
                "data": {
                    "execution_mode": "Alpaca Paper Trading",
                    "order_status": "Blocked",
                    "reason": "Risk approval is required before execution.",
                },
            }

        if side not in ["BUY", "SELL"]:
            return {
                "agent": "Execution Agent",
                "status": "blocked",
                "summary": "Execution Agent blocked the order because no valid trade direction was provided.",
                "data": {
                    "execution_mode": "Alpaca Paper Trading",
                    "order_status": "Blocked",
                    "reason": "A valid BUY or SELL direction is required before execution.",
                },
            }

        if approved_quantity <= 0:
            return {
                "agent": "Execution Agent",
                "status": "blocked",
                "summary": "Execution Agent blocked the order because the approved quantity is zero.",
                "data": {
                    "execution_mode": "Alpaca Paper Trading",
                    "order_status": "Blocked",
                    "reason": "Approved quantity must be greater than zero.",
                },
            }

        order = submit_paper_market_order(
            symbol=ticker,
            qty=approved_quantity,
            side=side
        )

        return {
            "agent": "Execution Agent",
            "status": "complete",
            "summary": f"Paper order submitted for {approved_quantity} {ticker}.",
            "data": {
                "execution_mode": "Alpaca Paper Trading",
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
            "summary": f"Execution Agent failed: {str(e)}",
            "data": {
                "execution_mode": "Alpaca Paper Trading",
                "order_status": "Error",
                "reason": str(e),
            },
        }
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
                "summary": "Execution Agent held the order because pre-trade risk approval was not granted.",
                "data": {
                    "execution_mode": "Alpaca Paper Trading",
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
                    "execution_mode": "Alpaca Paper Trading",
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
                    "execution_mode": "Alpaca Paper Trading",
                    "order_status": "Blocked",
                    "reason": "Approved quantity must be greater than zero before the order can be submitted.",
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
            "summary": f"Execution Agent routed a {side} paper market order for {approved_quantity} share(s) of {ticker} to Alpaca.",
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
            "summary": f"Execution Agent could not complete paper order routing: {str(e)}",
            "data": {
                "execution_mode": "Alpaca Paper Trading",
                "order_status": "Error",
                "reason": f"Alpaca paper order routing failed before confirmation: {str(e)}",
            },
        }
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce


def enum_to_text(value):
    if hasattr(value, "value"):
        return str(value.value)

    return str(value)

def get_trading_client(alpaca_credentials=None) -> TradingClient:
    if alpaca_credentials:
        api_key = alpaca_credentials.get("api_key")
        api_secret = alpaca_credentials.get("secret_key")
    else:
        api_key = st.secrets["ALPACA_API_KEY"]
        api_secret = st.secrets["ALPACA_API_SECRET"]

    if not api_key or not api_secret:
        raise ValueError("Alpaca Paper API Key and Secret Key are required.")

    return TradingClient(
        api_key,
        api_secret,
        paper=True
    )


def check_alpaca_connection(alpaca_credentials=None) -> dict:
    try:
        client = get_trading_client(alpaca_credentials=alpaca_credentials)
        account = client.get_account()

        return {
            "status": "connected",
            "account_id": str(account.id),
            "account_status": str(account.status),
            "buying_power": str(account.buying_power),
            "cash": str(account.cash),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Alpaca paper trading connection could not be established: {str(e)}",
        }

def submit_paper_market_order(symbol: str, qty: int, side: str, alpaca_credentials: dict | None = None,) -> dict:
    client = get_trading_client(alpaca_credentials)

    if side.upper() == "BUY":
        order_side = OrderSide.BUY
    elif side.upper() == "SELL":
        order_side = OrderSide.SELL
    else:
        raise ValueError("Order side must be BUY or SELL before routing to Alpaca.")

    order_data = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=order_side,
        time_in_force=TimeInForce.DAY
    )

    order = client.submit_order(order_data=order_data)

    order_type = getattr(order, "order_type", None)

    if order_type is None:
        order_type = getattr(order, "type", "market")

    return {
        "order_id": str(getattr(order, "id", "")),
        "client_order_id": str(getattr(order, "client_order_id", "")),
        "symbol": str(getattr(order, "symbol", symbol)),
        "qty": str(getattr(order, "qty", qty)),
        "side": enum_to_text(getattr(order, "side", side)),
        "status": enum_to_text(getattr(order, "status", "submitted")),
        "order_type": enum_to_text(order_type),
        "time_in_force": enum_to_text(getattr(order, "time_in_force", "day")),
        "submitted_at": str(getattr(order, "submitted_at", "")),
    }
import re

COMPANY_TO_TICKER = {
    "apple": "AAPL",
    "aapl": "AAPL",
    "nvidia": "NVDA",
    "nvda": "NVDA",
    "tesla": "TSLA",
    "tsla": "TSLA",
    "microsoft": "MSFT",
    "msft": "MSFT",
    "amazon": "AMZN",
    "amzn": "AMZN",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "meta": "META",
    "facebook": "META",
}


def extract_ticker(query: str) -> str:
    query_lower = query.lower()

    for company_name, ticker in COMPANY_TO_TICKER.items():
        if company_name in query_lower:
            return ticker

    possible_tickers = re.findall(r"\b[A-Z]{1,5}\b", query)

    if possible_tickers:
        return possible_tickers[0]

    return "AAPL"

def extract_quantity(query: str) -> int:
    numbers = re.findall(r"\b\d+\b", query)

    if numbers:
        return int(numbers[0])

    return 10

def extract_side(query: str) -> str:
    query_lower = query.lower()

    if any(word in query_lower for word in ["sell", "short", "exit"]):
        return "SELL"

    if any(word in query_lower for word in ["buy", "long", "need", "purchase"]):
        return "BUY"

    return "ANALYSE"
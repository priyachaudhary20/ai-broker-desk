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
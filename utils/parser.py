import re

COMPANY_TO_TICKER = {
    #Mega-cap technology
    "apple": "AAPL",
    "aapl": "AAPL",
    "microsoft": "MSFT",
    "msft": "MSFT",
    "nvidia": "NVDA",
    "nvda": "NVDA",
    "amazon": "AMZN",
    "amzn": "AMZN",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "googl": "GOOGL",
    "meta": "META",
    "facebook": "META",
    "tesla": "TSLA",
    "tsla": "TSLA",

    # Semiconductors
    "amd": "AMD",
    "advanced micro devices": "AMD",
    "intel": "INTC",
    "intc": "INTC",
    "broadcom": "AVGO",
    "avgo": "AVGO",
    "qualcomm": "QCOM",
    "qcom": "QCOM",
    "micron": "MU",
    "mu": "MU",
    "arm": "ARM",

    # Software and cloud
    "oracle": "ORCL",
    "orcl": "ORCL",
    "salesforce": "CRM",
    "crm": "CRM",
    "adobe": "ADBE",
    "adbe": "ADBE",
    "servicenow": "NOW",
    "snowflake": "SNOW",
    "snow": "SNOW",
    "palantir": "PLTR",
    "pltr": "PLTR",

    # Financials
    "jpmorgan": "JPM",
    "jp morgan": "JPM",
    "jpm": "JPM",
    "goldman": "GS",
    "goldman sachs": "GS",
    "gs": "GS",
    "morgan stanley": "MS",
    "bank of america": "BAC",
    "bac": "BAC",
    "visa": "V",
    "mastercard": "MA",

    # Consumer and retail
    "walmart": "WMT",
    "wmt": "WMT",
    "costco": "COST",
    "cost": "COST",
    "mcdonalds": "MCD",
    "mcdonald's": "MCD",
    "mcd": "MCD",
    "starbucks": "SBUX",
    "sbux": "SBUX",
    "nike": "NKE",
    "nke": "NKE",

    # Healthcare
    "eli lilly": "LLY",
    "lilly": "LLY",
    "johnson and johnson": "JNJ",
    "jnj": "JNJ",
    "unitedhealth": "UNH",
    "united health": "UNH",
    "unh": "UNH",
    "pfizer": "PFE",
    "pfe": "PFE",
    "moderna": "MRNA",
    "mrna": "MRNA",

    # Energy and industrials
    "exxon": "XOM",
    "exxon mobil": "XOM",
    "xom": "XOM",
    "chevron": "CVX",
    "cvx": "CVX",
    "boeing": "BA",
    "ba": "BA",
    "caterpillar": "CAT",
    "cat": "CAT",
    "general electric": "GE",
    "ge": "GE",

    # Media and platforms
    "netflix": "NFLX",
    "nflx": "NFLX",
    "disney": "DIS",
    "dis": "DIS",
    "uber": "UBER",
    "airbnb": "ABNB",
    "abnb": "ABNB",
    "coinbase": "COIN",
    "coin": "COIN",
}


def extract_ticker(query: str) -> str:
    query_lower = query.lower()

    for company_name, ticker in COMPANY_TO_TICKER.items():
        if company_name in query_lower:
            return ticker

    possible_tickers = re.findall(r"\b[A-Z]{2,5}\b", query)

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

    if any(word in query_lower for word in ["buy", "long", "purchase", "acquire"]):
        return "BUY"

    return "ANALYSE"
import yfinance as yf


POSITIVE_WORDS = [
    "beat",
    "beats",
    "growth",
    "upgrade",
    "upgraded",
    "surge",
    "surges",
    "record",
    "strong",
    "profit",
    "profits",
    "bullish",
    "positive",
    "rally",
    "rises",
    "gain",
    "gains",
    "outperform",
    "demand",
]

NEGATIVE_WORDS = [
    "miss",
    "misses",
    "fall",
    "falls",
    "drop",
    "drops",
    "downgrade",
    "downgraded",
    "weak",
    "loss",
    "losses",
    "bearish",
    "negative",
    "lawsuit",
    "probe",
    "cut",
    "cuts",
    "slump",
    "warning",
]


def score_sentiment(text: str) -> int:
    text = text.lower()

    positive_hits = sum(1 for word in POSITIVE_WORDS if word in text)
    negative_hits = sum(1 for word in NEGATIVE_WORDS if word in text)

    score = 50 + (positive_hits * 8) - (negative_hits * 8)

    return max(0, min(100, score))


def extract_headline(news_item: dict) -> str | None:
    if not isinstance(news_item, dict):
        return None

    if news_item.get("title"):
        return news_item["title"]

    content = news_item.get("content")

    if isinstance(content, dict):
        if content.get("title"):
            return content["title"]

    return None


def extract_link(news_item: dict) -> str | None:
    """
    yfinance news objects can return links in different shapes.
    This function checks common locations safely.
    """

    if not isinstance(news_item, dict):
        return None

    # Older/simple yfinance structure
    if news_item.get("link"):
        return news_item["link"]

    if news_item.get("url"):
        return news_item["url"]

    content = news_item.get("content")

    if isinstance(content, dict):
        # Common newer nested structures
        canonical_url = content.get("canonicalUrl")
        if isinstance(canonical_url, dict) and canonical_url.get("url"):
            return canonical_url["url"]

        click_url = content.get("clickThroughUrl")
        if isinstance(click_url, dict) and click_url.get("url"):
            return click_url["url"]

        if content.get("url"):
            return content["url"]

    return None


def run_news_agent(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)

        try:
            news_items = stock.news
        except Exception:
            news_items = []

        articles = []

        for item in news_items[:5]:
            headline = extract_headline(item)
            link = extract_link(item)

            if headline:
                articles.append({
                    "title": headline,
                    "link": link
                })

        headlines = [article["title"] for article in articles]

        if not headlines:
            return {
                "agent": "News Agent",
                "status": "complete",
                "summary": f"News Agent found no recent headlines for {ticker}. Headline sentiment is treated as Neutral for this run.",
                "data": {
                    "ticker": ticker,
                    "sentiment": "Neutral",
                    "sentiment_score": 50,
                    "articles": [],
                    "headlines": [],
                },
            }

        combined_text = " ".join(headlines)
        sentiment_score = score_sentiment(combined_text)

        if sentiment_score >= 65:
            sentiment = "Positive"
        elif sentiment_score <= 40:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        return {
            "agent": "News Agent",
            "status": "complete",
            "summary": f"News Agent reads headline tone for {ticker} as {sentiment} with a sentiment score of {sentiment_score}/100 across {len(headlines)} recent headline(s).",
            "data": {
                "ticker": ticker,
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "articles": articles,
                "headlines": headlines,
            },
        }

    except Exception as e:
        return {
            "agent": "News Agent",
            "status": "error",
            "summary": f"News Agent could not complete the headline review for {ticker}: {str(e)}",
            "data": {
                "ticker": ticker,
                "sentiment": "Neutral",
                "sentiment_score": 50,
                "articles": [],
                "headlines": [],
            },
        }
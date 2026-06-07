import streamlit as st

from utils.parser import extract_ticker
from agents.market_agent import run_market_agent
from agents.news_agent import run_news_agent


st.set_page_config(
    page_title="AI Broker Desk",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI Broker Desk")
st.caption("Phase 2: Market Agent + News Agent")

st.warning(
    "Demo only. This app does not provide financial advice and does not execute real trades."
)

query = st.text_input(
    "Enter your broker request:",
    placeholder="Example: What's happening with Nvidia?"
)

if st.button("Run Agents", type="primary"):
    if not query:
        st.error("Please enter a request first.")
    else:
        ticker = extract_ticker(query)

        st.write(f"Detected ticker: **{ticker}**")

        with st.spinner("Market Agent is analysing market data..."):
            market_result = run_market_agent(ticker)

        with st.spinner("News Agent is analysing recent headlines..."):
            news_result = run_news_agent(ticker)

        st.subheader("🤖 Agent Activity Panel")

        col_a, col_b = st.columns(2)

        with col_a:
            if market_result["status"] == "complete":
                st.success("Market Agent complete ✅")
                st.write(market_result["summary"])
            else:
                st.error("Market Agent failed ❌")
                st.write(market_result["summary"])

        with col_b:
            if news_result["status"] == "complete":
                st.success("News Agent complete ✅")
                st.write(news_result["summary"])
            else:
                st.error("News Agent failed ❌")
                st.write(news_result["summary"])

        st.divider()

        if market_result["status"] == "complete":
            market_data = market_result["data"]

            st.subheader("📊 Market Analysis")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Ticker", market_data["ticker"])

            with col2:
                st.metric("Latest Price", f"${market_data['latest_price']}")

            with col3:
                st.metric("Daily Change", f"{market_data['daily_change_pct']}%")

            st.write(f"**Trend:** {market_data['trend']}")
            st.write(f"**20-Day Moving Average:** ${market_data['ma20']}")
            st.write(f"**50-Day Moving Average:** ${market_data['ma50']}")
            st.write(f"**Trend Score:** {market_data['trend_score']}/100")

        st.divider()

        if news_result["status"] == "complete":
            news_data = news_result["data"]

            st.subheader("📰 News Sentiment")

            col4, col5 = st.columns(2)

            with col4:
                st.metric("Sentiment", news_data["sentiment"])

            with col5:
                st.metric("Sentiment Score", f"{news_data['sentiment_score']}%")

            st.write("**Recent Headlines:**")

            articles = news_data.get("articles", [])

            if articles:
                for article in articles:
                    title = article.get("title")
                    link = article.get("link")

                    if link:
                        st.markdown(f"- [{title}]({link})")
                    else:
                        st.write(f"- {title}")
            else:
                st.info("No recent headlines found. Sentiment treated as Neutral.")

        st.divider()

        with st.expander("Raw Agent Outputs"):
            st.write("Market Agent Output")
            st.json(market_result)

            st.write("News Agent Output")
            st.json(news_result)
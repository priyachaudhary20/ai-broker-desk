import streamlit as st

from utils.parser import extract_ticker
from agents.market_agent import run_market_agent


st.set_page_config(
    page_title="AI Broker Desk",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI Broker Desk")
st.caption("Phase 1: Market Agent Demo")

st.warning(
    "Demo only. This app does not provide financial advice and does not execute real trades."
)

query = st.text_input(
    "Enter your broker request:",
    placeholder="Example: Should I buy Apple today?"
)

if st.button("Run Market Agent", type="primary"):
    if not query:
        st.error("Please enter a request first.")
    else:
        ticker = extract_ticker(query)

        st.write(f"Detected ticker: **{ticker}**")

        with st.spinner("Market Agent is analysing market data..."):
            result = run_market_agent(ticker)

        if result["status"] == "complete":
            st.success("Market Agent complete ✅")

            data = result["data"]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Ticker", data["ticker"])

            with col2:
                st.metric("Latest Price", f"${data['latest_price']}")

            with col3:
                st.metric("Daily Change", f"{data['daily_change_pct']}%")

            st.subheader("Market Analysis")

            st.write(f"**Trend:** {data['trend']}")
            st.write(f"**20-Day Moving Average:** ${data['ma20']}")
            st.write(f"**50-Day Moving Average:** ${data['ma50']}")
            st.write(f"**Trend Score:** {data['trend_score']}/100")

            st.info(result["summary"])

            with st.expander("Raw Agent Output"):
                st.json(result)

        else:
            st.error(result["summary"])
            st.json(result)
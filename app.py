import streamlit as st

from utils.parser import extract_ticker, extract_quantity, extract_side
from agents.market_agent import run_market_agent
from agents.news_agent import run_news_agent
from agents.strategy_agent import run_strategy_agent
from agents.risk_agent import run_risk_agent
from agents.execution_agent import run_execution_agent
from brokers.alpaca_client import check_alpaca_connection

st.set_page_config(
    page_title="AI Broker Desk",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI Broker Desk")
st.caption("Phase 5: Market + News + Strategy + Risk + Alpaca Paper Execution")

st.warning(
    "Demo only. This app does not provide financial advice and does not execute real trades."
)

with st.sidebar:
    st.subheader("Execution Settings")
    st.write("Mode: **Alpaca Paper Trading**")
    st.write("Live Trading: **Disabled**")
    st.write("Real Money: **No**")

    if st.button("Check Alpaca Connection"):
        connection = check_alpaca_connection()

        if connection["status"] == "connected":
            st.success("Alpaca connected ✅")
            st.write(f"Account Status: {connection['account_status']}")
            st.write(f"Buying Power: ${connection['buying_power']}")
            st.write(f"Cash: ${connection['cash']}")
        else:
            st.error("Alpaca connection failed ❌")
            st.write(connection["message"])

query = st.text_input(
    "Enter your broker request:",
    placeholder="Example: What's happening with Nvidia?"
)

if st.button("Run Agents", type="primary"):
    if not query:
        st.error("Please enter a request first.")
    else:
        ticker = extract_ticker(query)
        requested_quantity = extract_quantity(query)
        side = extract_side(query)

        st.write(f"Detected ticker: **{ticker}**")
        st.write(f"Detected side: **{side}**")
        st.write(f"Requested quantity: **{requested_quantity}**")

        with st.spinner("Market Agent is analysing market data..."):
            market_result = run_market_agent(ticker)

        with st.spinner("News Agent is analysing recent headlines..."):
            news_result = run_news_agent(ticker)

        if market_result["status"] == "complete" and news_result["status"] == "complete":
            with st.spinner("Strategy Agent is evaluating entry conditions..."):
                strategy_result = run_strategy_agent(
                    market_result["data"],
                    news_result["data"]
                )
        else:
            strategy_result = {
                "agent": "Strategy Agent",
                "status": "blocked",
                "summary": "Strategy Agent blocked because Market or News Agent failed.",
                "data": {
                    "signal": "HOLD",
                    "confidence": 50,
                    "reason": "Insufficient data for strategy decision.",
                },
            }

        if strategy_result["status"] == "complete":
            with st.spinner("Risk Agent is checking position size and controls..."):
                risk_result = run_risk_agent(
                    market_result["data"],
                    strategy_result["data"],
                    requested_quantity,
                    side
                )
        else:
            risk_result = {
                "agent": "Risk Agent",
                "status": "blocked",
                "summary": "Risk Agent was blocked because the strategy decision was unavailable.",
                "data": {
                    "approval": "Blocked",
                    "risk_level": "High",
                    "reason": "Strategy data is unavailable. The trade has been blocked.",
                },
            }

        with st.spinner("Execution Agent is processing the paper order..."):
            execution_result = run_execution_agent(risk_result["data"])

        st.subheader("🤖 Agent Activity Panel")

        col_a, col_b, col_c, col_d, col_e = st.columns(5)

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

        with col_c:
            if strategy_result["status"] == "complete":
                st.success("Strategy Agent complete ✅")
                st.write(strategy_result["summary"])
            else:
                st.warning("Strategy Agent blocked ⚠️")
                st.write(strategy_result["summary"])

        with col_d:
            if risk_result["data"].get("approval") == "Approved":
                st.success("Risk Agent ✅")
                st.write(risk_result["summary"])
            else:
                st.warning("Risk Agent ⚠️")
                st.write(risk_result["summary"])

        with col_e:
            if execution_result["status"] == "complete":
                st.success("Execution Agent ✅")
                st.write(execution_result["summary"])
            elif execution_result["status"] == "blocked":
                st.warning("Execution Agent ⚠️")
                st.write(execution_result["summary"])
            else:
                st.error("Execution Agent ❌")
                st.write(execution_result["summary"])

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
                st.info("No recent headlines found. Sentiment has been treated as Neutral.")

        st.divider()

        st.subheader("🧠 Strategy / Entry Decision")

        strategy_data = strategy_result["data"]

        col6, col7, col8 = st.columns(3)

        with col6:
            st.metric("Entry Signal", strategy_data.get("signal", "HOLD"))

        with col7:
            st.metric("Confidence", f"{strategy_data.get('confidence', 50)}%")

        with col8:
            st.metric("Volatility", strategy_data.get("volatility_status", "Unknown"))

        st.write("**Reason:**")
        st.info(strategy_data.get("reason", "No reason is available."))

        st.divider()

        st.subheader("🛡️ Risk Assessment")

        risk_data = risk_result["data"]

        col9, col10, col11, col12 = st.columns(4)

        with col9:
            st.metric("Approval", risk_data.get("approval", "Blocked"))

        with col10:
            st.metric("Risk Level", risk_data.get("risk_level", "High"))

        with col11:
            st.metric("Approved Qty", risk_data.get("approved_quantity", 0))

        with col12:
            st.metric("Notional", f"${risk_data.get('notional', 0)}")

        col13, col14, col15 = st.columns(3)

        with col13:
            st.metric("Requested Qty", risk_data.get("requested_quantity", requested_quantity))

        with col14:
            stop_loss = risk_data.get("stop_loss")

            if stop_loss:
                st.metric("Stop Loss", f"${stop_loss}")
            else:
                st.metric("Stop Loss", "N/A")

        with col15:
            st.metric("Risk Score", f"{risk_data.get('risk_score', 0)}/100")

        st.write("**Risk Reason:**")
        st.info(risk_data.get("reason", "No risk reason is available."))

        st.divider()

        st.subheader("⚡ Paper Execution")

        execution_data = execution_result["data"]

        col16, col17, col18 = st.columns(3)

        with col16:
            st.metric("Execution Mode", execution_data.get("execution_mode", "Paper"))

        with col17:
            st.metric("Order Status", execution_data.get("order_status", "N/A"))

        with col18:
            st.metric("Quantity", execution_data.get("quantity", "N/A"))

        if execution_result["status"] == "complete":
            st.success("Paper order submitted successfully.")
            st.write(f"**Order ID:** {execution_data.get('order_id')}")
            st.write(f"**Client Order ID:** {execution_data.get('client_order_id')}")
            st.write(f"**Ticker:** {execution_data.get('ticker')}")
            st.write(f"**Side:** {execution_data.get('side')}")
            st.write(f"**Order Type:** {execution_data.get('order_type')}")
            st.write(f"**Time in Force:** {execution_data.get('time_in_force')}")
            st.write(f"**Submitted At:** {execution_data.get('submitted_at')}")
        elif execution_result["status"] == "blocked":
            st.warning(execution_data.get("reason", "Execution was blocked."))
        else:
            st.error(execution_data.get("reason", "Execution failed."))

        st.divider()

        with st.expander("Raw Agent Outputs"):
            st.write("Market Agent Output")
            st.json(market_result)

            st.write("News Agent Output")
            st.json(news_result)

            st.write("Strategy Agent Output")
            st.json(strategy_result)

            st.write("Risk Agent Output")
            st.json(risk_result)

            st.write("Execution Agent Output")
            st.json(execution_result)
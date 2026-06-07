import streamlit as st

from agents.broker_orchestrator import run_broker_workflow
from brokers.alpaca_client import check_alpaca_connection

st.set_page_config(
    page_title="AI Broker Desk",
    page_icon="📈",
    layout="wide"
)

st.markdown(
    """
    <style>
        .main-header {
            padding: 1.2rem 1.4rem;
            border-radius: 16px;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #111827 100%);
            color: white;
            margin-bottom: 1.2rem;
            border: 1px solid rgba(255,255,255,0.08);
        }

        .main-header h1 {
            margin: 0;
            font-size: 2.1rem;
            font-weight: 750;
        }

        .main-header p {
            margin-top: 0.4rem;
            color: #cbd5e1;
            font-size: 0.98rem;
        }

        .status-card {
            padding: 1rem;
            border-radius: 14px;
            border: 1px solid #e5e7eb;
            background: #ffffff;
            min-height: 150px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }

        .status-title {
            font-size: 0.95rem;
            font-weight: 700;
            color: #111827;
            margin-bottom: 0.35rem;
        }

        .status-text {
            font-size: 0.87rem;
            color: #374151;
            line-height: 1.35;
        }

        .badge-success {
            display: inline-block;
            padding: 0.18rem 0.55rem;
            border-radius: 999px;
            background: #dcfce7;
            color: #166534;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 0.55rem;
        }

        .badge-warning {
            display: inline-block;
            padding: 0.18rem 0.55rem;
            border-radius: 999px;
            background: #fef3c7;
            color: #92400e;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 0.55rem;
        }

        .badge-error {
            display: inline-block;
            padding: 0.18rem 0.55rem;
            border-radius: 999px;
            background: #fee2e2;
            color: #991b1b;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 0.55rem;
        }

        .badge-neutral {
            display: inline-block;
            padding: 0.18rem 0.55rem;
            border-radius: 999px;
            background: #e0f2fe;
            color: #075985;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 0.55rem;
        }

        .info-box {
            padding: 1rem;
            border-radius: 14px;
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
        }

        .small-muted {
            color: #64748b;
            font-size: 0.86rem;
        }

        .section-title {
            font-size: 1.1rem;
            font-weight: 750;
            color: #111827;
            margin-top: 0.5rem;
            margin-bottom: 0.8rem;
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            padding: 0.85rem;
            border-radius: 14px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }
    </style>
    """,
    unsafe_allow_html=True
)

def badge_for_agent(agent_result: dict, agent_type: str = "generic") -> tuple[str, str]:
    status = agent_result.get("status", "unknown")

    if status == "complete":
        return "Complete", "badge-success"

    if status == "disabled":
        return "Disabled", "badge-neutral"

    if status == "blocked":
        return "Blocked", "badge-warning"

    if status == "error":
        return "Error", "badge-error"

    if agent_type == "risk":
        approval = agent_result.get("data", {}).get("approval", "")
        if str(approval).startswith("Approved"):
            return "Approved", "badge-success"
        return "Blocked", "badge-warning"

    return status.title(), "badge-neutral"


def render_agent_card(title: str, agent_result: dict, agent_type: str = "generic") -> None:
    label, badge_class = badge_for_agent(agent_result, agent_type)
    summary = agent_result.get("summary", "No summary available.")

    st.markdown(
        f"""
        <div class="status-card">
            <div class="{badge_class}">{label}</div>
            <div class="status-title">{title}</div>
            <div class="status-text">{summary}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def safe_metric_value(value, default="N/A"):
    if value is None:
        return default
    return value

st.markdown(
    """
    <div class="main-header">
        <h1>AI Broker Desk</h1>
        <p>Multi-agent broker workflow for market analysis, news sentiment, strategy, risk control, and Alpaca paper execution.</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.warning(
    "Demo only. This app does not provide financial advice. Alpaca orders are submitted to paper trading only when explicitly enabled."
)

with st.sidebar:
    st.subheader("Execution Controls")

    st.markdown(
        """
        **Mode:** Alpaca Paper Trading  
        **Live Trading:** Disabled  
        **Real Money:** No
        """
    )

    submit_paper_order = st.checkbox(
        "Submit paper order to Alpaca",
        value=False,
        help="Keep this off while testing. Turn it on only when you want to submit a real paper order."
    )

    if submit_paper_order:
        st.warning("Paper execution is enabled. Approved trades will be submitted to Alpaca paper trading.")
    else:
        st.info("Paper execution is disabled. The workflow will run without submitting orders.")

    st.divider()

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

    st.divider()

    st.subheader("Demo Queries")
    st.caption("Try examples like:")
    st.code("Need 10 AAPL around market")
    st.code("Should I buy Nvidia today?")
    st.code("Analyse Microsoft")
    st.code("Need 100 Tesla around market")

st.markdown('<div class="section-title">Broker Request</div>', unsafe_allow_html=True)

with st.form("broker_request_form"):
    query = st.text_input(
        "Enter your broker request",
        placeholder="Example: Need 10 AAPL around market"
    )

    run_button = st.form_submit_button("Run Broker Workflow", type="primary")

if run_button:
    if not query:
        st.error("Please enter a broker request first.")
    else:
        with st.spinner("Broker Orchestrator is running the agent workflow..."):
            st.session_state["workflow_result"] = run_broker_workflow(
                query=query,
                submit_paper_order=submit_paper_order
            )


workflow_result = st.session_state.get("workflow_result")

if workflow_result:
    parsed = workflow_result["parsed_request"]
    final_decision = workflow_result["final_decision"]
    agents = workflow_result["agents"]

    market_result = agents["market"]
    news_result = agents["news"]
    strategy_result = agents["strategy"]
    risk_result = agents["risk"]
    execution_result = agents["execution"]

    market_data = market_result.get("data", {})
    news_data = news_result.get("data", {})
    strategy_data = strategy_result.get("data", {})
    risk_data = risk_result.get("data", {})
    execution_data = execution_result.get("data", {})

    st.divider()

    st.markdown('<div class="section-title">Broker Decision Summary</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Ticker", parsed.get("ticker", "N/A"))

    with col2:
        st.metric("Side", parsed.get("side", "N/A"))

    with col3:
        st.metric("Requested Qty", parsed.get("requested_quantity", "N/A"))

    with col4:
        st.metric("Execution Status", final_decision.get("execution_status", "N/A"))

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.metric("Strategy Signal", final_decision.get("strategy_signal", "N/A"))

    with col6:
        st.metric("Confidence", f"{final_decision.get('confidence', 0)}%")

    with col7:
        st.metric("Risk Approval", final_decision.get("risk_approval", "N/A"))

    with col8:
        st.metric("Execution Mode", execution_data.get("execution_mode", "Paper"))

    st.divider()
    st.markdown('<div class="section-title">Agent Activity Panel</div>', unsafe_allow_html=True)

    agent_col1, agent_col2, agent_col3, agent_col4, agent_col5 = st.columns(5)

    with agent_col1:
        render_agent_card("Market Agent", market_result)

    with agent_col2:
        render_agent_card("News Agent", news_result)

    with agent_col3:
        render_agent_card("Strategy Agent", strategy_result)

    with agent_col4:
        render_agent_card("Risk Agent", risk_result, agent_type="risk")

    with agent_col5:
        render_agent_card("Execution Agent", execution_result)

    st.divider()

    tab_market, tab_news, tab_strategy, tab_risk, tab_execution, tab_audit, tab_raw = st.tabs(
        [
            "Market",
            "News",
            "Strategy",
            "Risk",
            "Execution",
            "Audit Trail",
            "Raw Output"
        ]
    )

    with tab_market:
        st.subheader("Market Analysis")

        if market_result["status"] == "complete":
            m1, m2, m3 = st.columns(3)

            with m1:
                st.metric("Latest Price", f"${market_data.get('latest_price', 'N/A')}")

            with m2:
                st.metric("Daily Change", f"{market_data.get('daily_change_pct', 'N/A')}%")

            with m3:
                st.metric("Trend", market_data.get("trend", "N/A"))

            m4, m5, m6 = st.columns(3)

            with m4:
                st.metric("20-Day Moving Average", f"${market_data.get('ma20', 'N/A')}")

            with m5:
                st.metric("50-Day Moving Average", f"${market_data.get('ma50', 'N/A')}")

            with m6:
                st.metric("Trend Score", f"{market_data.get('trend_score', 'N/A')}/100")

            st.info(market_result.get("summary", "No market summary available."))
        else:
            st.error(market_result.get("summary", "Market Agent did not complete."))

    with tab_news:
        st.subheader("News Sentiment")

        if news_result["status"] == "complete":
            n1, n2 = st.columns(2)

            with n1:
                st.metric("Sentiment", news_data.get("sentiment", "N/A"))

            with n2:
                st.metric("Sentiment Score", f"{news_data.get('sentiment_score', 'N/A')}%")

            st.markdown("#### Recent Headlines")

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

            st.info(news_result.get("summary", "No news summary available."))
        else:
            st.error(news_result.get("summary", "News Agent did not complete."))

    with tab_strategy:
        st.subheader("Strategy / Entry Decision")

        s1, s2, s3 = st.columns(3)

        with s1:
            st.metric("Entry Signal", strategy_data.get("signal", "HOLD"))

        with s2:
            st.metric("Confidence", f"{strategy_data.get('confidence', 50)}%")

        with s3:
            st.metric("Volatility", strategy_data.get("volatility_status", "Unknown"))

        s4, s5, s6 = st.columns(3)

        with s4:
            st.metric("Trend Score", f"{strategy_data.get('trend_score', 'N/A')}/100")

        with s5:
            st.metric("Sentiment Score", f"{strategy_data.get('sentiment_score', 'N/A')}/100")

        with s6:
            st.metric("Volatility Score", f"{strategy_data.get('volatility_score', 'N/A')}/100")

        st.markdown("#### Strategy Reason")
        st.info(strategy_data.get("reason", "No strategy reason is available."))

    with tab_risk:
        st.subheader("Risk Assessment")

        r1, r2, r3, r4 = st.columns(4)

        with r1:
            st.metric("Approval", risk_data.get("approval", "Blocked"))

        with r2:
            st.metric("Risk Level", risk_data.get("risk_level", "High"))

        with r3:
            st.metric("Requested Qty", risk_data.get("requested_quantity", parsed.get("requested_quantity", "N/A")))

        with r4:
            st.metric("Approved Qty", risk_data.get("approved_quantity", 0))

        r5, r6, r7, r8 = st.columns(4)

        with r5:
            st.metric("Notional", f"${risk_data.get('notional', 0)}")

        with r6:
            stop_loss = risk_data.get("stop_loss")
            st.metric("Stop Loss", f"${stop_loss}" if stop_loss else "N/A")

        with r7:
            st.metric("Risk Score", f"{risk_data.get('risk_score', 0)}/100")

        with r8:
            st.metric("Max Demo Notional", f"${risk_data.get('max_demo_notional', 0)}")

        st.markdown("#### Risk Reason")
        st.info(risk_data.get("reason", "No risk reason is available."))

    with tab_execution:
        st.subheader("Paper Execution")

        e1, e2, e3 = st.columns(3)

        with e1:
            st.metric("Execution Mode", execution_data.get("execution_mode", "Paper"))

        with e2:
            st.metric("Order Status", execution_data.get("order_status", "N/A"))

        with e3:
            st.metric("Quantity", execution_data.get("quantity", "N/A"))

        if execution_result["status"] == "complete":
            st.success("Paper order submitted successfully.")

            detail_col1, detail_col2 = st.columns(2)

            with detail_col1:
                st.write(f"**Order ID:** {execution_data.get('order_id')}")
                st.write(f"**Client Order ID:** {execution_data.get('client_order_id')}")
                st.write(f"**Ticker:** {execution_data.get('ticker')}")
                st.write(f"**Side:** {execution_data.get('side')}")

            with detail_col2:
                st.write(f"**Order Type:** {execution_data.get('order_type')}")
                st.write(f"**Time in Force:** {execution_data.get('time_in_force')}")
                st.write(f"**Submitted At:** {execution_data.get('submitted_at')}")

            if execution_data.get("order_status") in ["accepted", "new"]:
                st.info("The order was accepted by Alpaca and may remain pending until the US market opens.")

        elif execution_result["status"] == "disabled":
            st.info(execution_data.get("reason", "Paper execution is disabled."))
        elif execution_result["status"] == "blocked":
            st.warning(execution_data.get("reason", "Execution was blocked."))
        else:
            st.error(execution_data.get("reason", "Execution failed."))

    with tab_audit:
        st.subheader("Audit Trail")

        audit_log = workflow_result.get("audit", [])

        if audit_log:
            for event in audit_log:
                st.write(f"• {event}")
        else:
            st.info("No audit events available.")

    with tab_raw:
        st.subheader("Raw Workflow Output")
        st.json(workflow_result)

else:
    st.markdown(
        """
        <div class="info-box">
            <b>Ready to run.</b><br>
            Enter a broker-style request above to start the workflow. Keep paper execution disabled while testing, then enable it when you want to submit an Alpaca paper order.
        </div>
        """,
        unsafe_allow_html=True
    )
from utils.parser import extract_ticker, extract_quantity, extract_side
from utils.audit import add_audit_event

from agents.market_agent import run_market_agent
from agents.news_agent import run_news_agent
from agents.strategy_agent import run_strategy_agent
from agents.risk_agent import run_risk_agent
from agents.execution_agent import run_execution_agent


def build_disabled_execution_result(reason: str) -> dict:
    return {
        "agent": "Execution Agent",
        "status": "disabled",
        "summary": "Execution Agent did not submit an order because paper execution is disabled.",
        "data": {
            "execution_mode": "Alpaca Paper Trading",
            "order_status": "Not Submitted",
            "reason": reason,
        },
    }


def run_broker_workflow(query: str, submit_paper_order: bool = False) -> dict:
    """
    Broker Orchestrator coordinates the full AI Broker Desk workflow.

    It controls:
    - Request parsing.
    - Market analysis.
    - News analysis.
    - Strategy decision.
    - Risk assessment.
    - Optional Alpaca paper execution.
    - Audit trail generation.
    """

    audit_log = []

    add_audit_event(audit_log, "User request received.")

    ticker = extract_ticker(query)
    requested_quantity = extract_quantity(query)
    side = extract_side(query)

    add_audit_event(
        audit_log,
        f"Request parsed as {side} {requested_quantity} {ticker}."
    )

    market_result = run_market_agent(ticker)
    add_audit_event(
        audit_log,
        f"Market Agent finished with status: {market_result.get('status')}."
    )

    news_result = run_news_agent(ticker)
    add_audit_event(
        audit_log,
        f"News Agent finished with status: {news_result.get('status')}."
    )

    if market_result["status"] == "complete" and news_result["status"] == "complete":
        strategy_result = run_strategy_agent(
            market_result["data"],
            news_result["data"]
        )
        add_audit_event(
            audit_log,
            f"Strategy Agent generated signal: {strategy_result['data'].get('signal', 'Unknown')}."
        )
    else:
        strategy_result = {
            "agent": "Strategy Agent",
            "status": "blocked",
            "summary": "Strategy Agent was blocked because market or news data was unavailable.",
            "data": {
                "signal": "HOLD",
                "confidence": 50,
                "reason": "There is insufficient data to make a strategy decision.",
            },
        }
        add_audit_event(
            audit_log,
            "Strategy Agent was blocked because required data was unavailable."
        )

    if strategy_result["status"] == "complete":
        risk_result = run_risk_agent(
            market_result["data"],
            strategy_result["data"],
            requested_quantity,
            side
        )
        add_audit_event(
            audit_log,
            f"Risk Agent returned approval status: {risk_result['data'].get('approval', 'Unknown')}."
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
        add_audit_event(
            audit_log,
            "Risk Agent was blocked because the strategy decision was unavailable."
        )

    if submit_paper_order:
        execution_result = run_execution_agent(risk_result["data"])

        if execution_result["status"] == "complete":
            order_status = execution_result["data"].get("order_status", "Unknown")
            order_id = execution_result["data"].get("order_id", "Unknown")

            add_audit_event(
                audit_log,
                f"Execution Agent submitted paper order. Status: {order_status}. Order ID: {order_id}."
            )

            if order_status in ["accepted", "new"]:
                add_audit_event(
                    audit_log,
                    "Order was accepted by Alpaca. It may remain pending until the US market opens."
                )

        elif execution_result["status"] == "blocked":
            add_audit_event(
                audit_log,
                "Execution Agent blocked the order because execution conditions were not met."
            )
        else:
            add_audit_event(
                audit_log,
                "Execution Agent failed while processing the paper order."
            )

    else:
        execution_result = build_disabled_execution_result(
            "Paper execution is disabled in the app. Enable it from the sidebar to submit a paper order."
        )
        add_audit_event(
            audit_log,
            "Execution Agent was skipped because paper execution is disabled."
        )

    final_decision = {
        "ticker": ticker,
        "side": side,
        "requested_quantity": requested_quantity,
        "strategy_signal": strategy_result["data"].get("signal", "HOLD"),
        "confidence": strategy_result["data"].get("confidence", 50),
        "risk_approval": risk_result["data"].get("approval", "Blocked"),
        "execution_status": execution_result["data"].get("order_status", "Not Submitted"),
    }

    add_audit_event(audit_log, "Broker workflow completed.")

    return {
        "query": query,
        "parsed_request": {
            "ticker": ticker,
            "side": side,
            "requested_quantity": requested_quantity,
        },
        "final_decision": final_decision,
        "agents": {
            "market": market_result,
            "news": news_result,
            "strategy": strategy_result,
            "risk": risk_result,
            "execution": execution_result,
        },
        "audit": audit_log,
    }
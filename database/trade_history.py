import json
import os
import sqlite3
from datetime import datetime


DB_PATH = "database/trades.db"


def init_db() -> None:
    os.makedirs("database", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS workflow_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            query TEXT,
            ticker TEXT,
            side TEXT,
            requested_quantity INTEGER,
            approved_quantity INTEGER,
            strategy_signal TEXT,
            confidence INTEGER,
            risk_approval TEXT,
            risk_level TEXT,
            execution_status TEXT,
            order_id TEXT,
            raw_json TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def save_workflow_run(workflow_result: dict) -> int:
    init_db()

    parsed = workflow_result.get("parsed_request", {})
    final_decision = workflow_result.get("final_decision", {})
    agents = workflow_result.get("agents", {})

    risk_data = agents.get("risk", {}).get("data", {})
    execution_data = agents.get("execution", {}).get("data", {})

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO workflow_runs (
            created_at,
            query,
            ticker,
            side,
            requested_quantity,
            approved_quantity,
            strategy_signal,
            confidence,
            risk_approval,
            risk_level,
            execution_status,
            order_id,
            raw_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            workflow_result.get("query"),
            parsed.get("ticker"),
            parsed.get("side"),
            parsed.get("requested_quantity"),
            risk_data.get("approved_quantity"),
            final_decision.get("strategy_signal"),
            final_decision.get("confidence"),
            final_decision.get("risk_approval"),
            risk_data.get("risk_level"),
            final_decision.get("execution_status"),
            execution_data.get("order_id"),
            json.dumps(workflow_result, default=str),
        ),
    )

    run_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return run_id


def get_recent_workflow_runs(limit: int = 20) -> list[dict]:
    init_db()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            created_at,
            query,
            ticker,
            side,
            requested_quantity,
            approved_quantity,
            strategy_signal,
            confidence,
            risk_approval,
            risk_level,
            execution_status,
            order_id
        FROM workflow_runs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_workflow_run_by_id(run_id: int) -> dict | None:
    init_db()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT raw_json
        FROM workflow_runs
        WHERE id = ?
        """,
        (run_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return json.loads(row["raw_json"])
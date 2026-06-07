from datetime import datetime

def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")

def add_audit_event(audit_log: list, message: str) -> None:
    audit_log.append(f"{timestamp()} — {message}")
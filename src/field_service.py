"""Field-service workflow: decide dispatch state, then publish an audit log."""

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class WorkOrder:
    work_order_id: str
    customer: str
    dispatch_status: str
    photo_count: int
    technician_note: str


def dispatch_decision(order: WorkOrder) -> str:
    """A photo-backed follow-up is ready only after the technician closes the job."""
    if order.dispatch_status == "completed" and order.photo_count > 0 and order.technician_note.strip():
        return "follow_up_ready"
    return "needs_follow_up"


def log_entry(order: WorkOrder) -> dict[str, Any]:
    return {
        "message": "field service work order updated",
        "level": "info",
        "service": "field-service",
        "environment": "demo",
        "work_order": asdict(order),
        "decision": dispatch_decision(order),
    }

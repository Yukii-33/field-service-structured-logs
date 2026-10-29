"""Runnable workflow: publish one work-order event and search it."""

from field_service import WorkOrder, log_entry
from infrai_logs import ingest, search_logs, whoami


def main() -> None:
    order = WorkOrder(
        work_order_id="WO-1042",
        customer="Northwind Facilities",
        dispatch_status="completed",
        photo_count=3,
        technician_note="Replaced the failed relay and confirmed the panel is clear.",
    )
    ingest([log_entry(order)], idempotency_key=f"work-order:{order.work_order_id}")
    print("decision:", order.work_order_id, log_entry(order)["decision"])
    print("credential:", whoami())
    print("matches:", search_logs(order.work_order_id))


if __name__ == "__main__":
    main()

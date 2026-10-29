from src.field_service import WorkOrder, dispatch_decision


def test_completed_order_with_photos_is_ready_for_follow_up() -> None:
    order = WorkOrder("WO-1042", "Northwind Facilities", "completed", 3, "Panel checked.")
    assert dispatch_decision(order) == "follow_up_ready"


def test_completed_order_without_photos_stays_open() -> None:
    order = WorkOrder("WO-1043", "Northwind Facilities", "completed", 0, "Panel checked.")
    assert dispatch_decision(order) == "needs_follow_up"

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from analytics import summarize_bill_history


def test_summarize_bill_history_returns_expected_totals():
    rows = [
        (1, "C001", "01/01/2025", "200", "1000", "A"),
        (2, "C002", "01/02/2025", "250", "1200", "B"),
        (3, "C003", "01/03/2025", "300", "1500", "C"),
    ]

    summary = summarize_bill_history(rows)

    assert summary["total_bills"] == 3
    assert summary["total_units"] == 750
    assert summary["total_amount"] == 3700
    assert summary["average_bill"] == 1233.33
    assert summary["average_units"] == 250.0
    assert summary["highest_bill"] == 1500
    assert summary["lowest_bill"] == 1000
    assert summary["trend"] == "up"


def test_summarize_bill_history_handles_empty_rows():
    summary = summarize_bill_history([])

    assert summary == {
        "total_bills": 0,
        "total_units": 0.0,
        "total_amount": 0.0,
        "average_bill": 0.0,
        "average_units": 0.0,
        "highest_bill": 0.0,
        "lowest_bill": 0.0,
        "trend": "stable",
    }

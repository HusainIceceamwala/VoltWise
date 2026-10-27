def summarize_bill_history(rows):
    if not rows:
        return {
            "total_bills": 0,
            "total_units": 0.0,
            "total_amount": 0.0,
            "average_bill": 0.0,
            "average_units": 0.0,
            "highest_bill": 0.0,
            "lowest_bill": 0.0,
            "trend": "stable",
        }

    amounts = []
    units = []

    for row in rows:
        try:
            amounts.append(float(row[4]))
        except (TypeError, ValueError):
            continue

        try:
            units.append(float(row[3]))
        except (TypeError, ValueError):
            continue

    if not amounts:
        return {
            "total_bills": len(rows),
            "total_units": sum(units),
            "total_amount": 0.0,
            "average_bill": 0.0,
            "average_units": 0.0 if not units else sum(units) / len(units),
            "highest_bill": 0.0,
            "lowest_bill": 0.0,
            "trend": "stable",
        }

    if len(amounts) >= 2:
        if amounts[-1] > amounts[0]:
            trend = "up"
        elif amounts[-1] < amounts[0]:
            trend = "down"
        else:
            trend = "stable"
    else:
        trend = "stable"

    return {
        "total_bills": len(rows),
        "total_units": round(sum(units), 2),
        "total_amount": round(sum(amounts), 2),
        "average_bill": round(sum(amounts) / len(amounts), 2),
        "average_units": round(sum(units) / len(units), 2) if units else 0.0,
        "highest_bill": round(max(amounts), 2),
        "lowest_bill": round(min(amounts), 2),
        "trend": trend,
    }

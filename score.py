def energy_score(units):

    try:
        units = float(units)
    except:
        return 0, "Unknown"

    if units < 150:
        return 95, "Excellent"

    elif units < 250:
        return 80, "Good"

    elif units < 400:
        return 65, "Average"

    else:
        return 40, "High Consumption"
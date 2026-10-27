"""Stock turnover formulas. Pure functions: no database, easy to test.

Definitions (from the plan):
- units sold     = total OUT quantity in the period (ADJUST and IN excluded)
- average stock  = (opening stock + closing stock) / 2
- turnover ratio = units sold / average stock
- days of stock  = days in the period / turnover ratio

When average stock is zero, or nothing sold, the ratio or days are None,
which the UI shows as "n/a".
"""


def average_stock(opening, closing):
    return (opening + closing) / 2


def turnover_ratio(units_sold, avg_stock):
    if avg_stock <= 0:
        return None
    return units_sold / avg_stock


def days_of_stock(period_days, ratio):
    if ratio is None or ratio <= 0:
        return None
    return period_days / ratio


def calculate(units_sold, opening, closing, period_days):
    """Return a dict with every turnover figure, rounded for display."""
    avg = average_stock(opening, closing)
    ratio = turnover_ratio(units_sold, avg)
    days = days_of_stock(period_days, ratio)
    return {
        "units_sold": units_sold,
        "opening_stock": opening,
        "closing_stock": closing,
        "average_stock": round(avg, 2),
        "turnover": round(ratio, 2) if ratio is not None else None,
        "days_of_stock": round(days, 1) if days is not None else None,
    }

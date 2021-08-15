import decimal


def to_decimal(value, default_value=0, precision=None):
    try:
        if precision:
            decimal.getcontext().prec = precision
        return decimal.Decimal(value)
    except Exception:
        return default_value

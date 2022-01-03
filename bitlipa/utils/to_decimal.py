import decimal


def to_decimal(value, precision=18, default_value=0):
    try:
        if precision:
            decimal.getcontext().prec = precision
        return decimal.Decimal(str(value))
    except Exception:
        return default_value

import decimal


def to_decimal(value, default_value=0, precision=18):
    try:
        if precision:
            decimal.getcontext().prec = precision
        return decimal.Decimal(str(value))
    except Exception:
        return default_value

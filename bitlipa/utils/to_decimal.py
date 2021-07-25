import decimal


def to_decimal(value, default_value=0):
    try:
        return decimal.Decimal(value)
    except Exception:
        return default_value

def to_float(value, default_value=0):
    try:
        return float(value)
    except Exception:
        return default_value

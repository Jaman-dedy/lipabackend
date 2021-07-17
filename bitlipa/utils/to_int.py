def to_int(value, default_value=0):
    try:
        return int(value)
    except Exception:
        return default_value

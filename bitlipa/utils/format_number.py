def format_number(value, default_value=0):
    try:
        return "{:.18f}".format(value).rstrip('0').rstrip('.')
    except Exception:
        return default_value

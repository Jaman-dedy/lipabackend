def format_number(value, decimal_places=18, default_value=0):
    try:
        dp = "{:." + str(decimal_places or 18) + "f}"
        return dp.format(value).rstrip('0').rstrip('.')
    except Exception:
        return default_value

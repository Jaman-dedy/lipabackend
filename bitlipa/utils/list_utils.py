def filter_list(values, fn=None, values_to_exclude=None):
    return list(filter(fn or (lambda k: k not in values_to_exclude or []), values))

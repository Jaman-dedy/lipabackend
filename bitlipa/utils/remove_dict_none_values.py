def remove_dict_none_values(d) -> dict:
    for key, value in dict(d).items():
        if value is None:
            del d[key]
    return d

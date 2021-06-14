def get_object_attr(obj, attr, default_value=None):
    try:
        return obj.__getattribute__(attr)
    except AttributeError:
        return default_value

from functools import reduce


def split_camel_case_words(str: str, separator: str = ' ') -> str:
    return reduce(lambda x, y: x + (separator if y.isupper() else '') + y, str)

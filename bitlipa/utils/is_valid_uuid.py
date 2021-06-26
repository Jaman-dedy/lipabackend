import uuid


def is_valid_uuid(val: str, version=4) -> bool:
    try:
        uuid_string = str(val).replace('-', '')
        uuid.UUID(uuid_string, version=4)
        return True
    except Exception:
        return False

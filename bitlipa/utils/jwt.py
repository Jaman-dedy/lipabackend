import jwt
import datetime
from bitlipa import settings


def encode(payload: dict, expiration_hours: int = 24) -> str:
    try:
        return jwt.encode({
            **payload, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expiration_hours)
        }, settings.SECRET_KEY, algorithm="HS256")

    except jwt.ExpiredSignatureError:
        return None


def decode(encoded_jwt: str) -> dict:
    try:
        return jwt.decode(encoded_jwt, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None

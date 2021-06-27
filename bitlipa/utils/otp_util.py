import pyotp


class OTPUtil:
    def generate(secret: str = None, digits: int = 6) -> str:
        totp = pyotp.TOTP(s=secret or pyotp.random_base32(), digits=digits)
        return totp.now()

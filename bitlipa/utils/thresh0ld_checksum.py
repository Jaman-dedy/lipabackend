from django.conf import settings
import time
from hashlib import sha256
import base64


class Thresh0ldChecksum:
    def __init__(self, secret, params=None, t=None, r=None, payload=None) -> None:
        self.secret = secret or ''
        self.params = params or []
        self.t = t or int(time.time())  # timestamp
        self.r = r or settings.APP_NAME  # random string
        self.payload = payload
        self.checksum = ''

    def __str__(self) -> str:
        return self.checksum

    def build(self) -> object:
        if self.payload:
            self.params.append(self.payload)

        self.params.append('t=%d' % self.t)
        self.params.append('r=%s' % self.r)
        self.params.sort()
        self.params.append('secret=%s' % self.secret)

        h = sha256()
        h.update(('&'.join(self.params)).encode('utf-8'))
        self.checksum = h.hexdigest()
        return self

    def calculate_callback(self) -> str:
        h = sha256()
        h.update((self.payload + self.secret).encode('utf-8'))
        return base64.urlsafe_b64encode(h.digest())

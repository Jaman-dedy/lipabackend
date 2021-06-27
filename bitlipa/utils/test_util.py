from django.contrib.auth.hashers import make_password

from bitlipa.apps.users.models import User


class TestUtil:
    def create_user():
        User(email="johnsmith@example.com",
             password="Password@123",
             phonenumber="+9999999999",
             pin=make_password("1234"),
             is_email_verified=True,
             is_phone_verified=True,
             ).save()

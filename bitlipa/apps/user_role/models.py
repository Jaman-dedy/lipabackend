from django.db import models
from uuid import uuid4

from .managers import UserRoleManager
from bitlipa.apps.users.models import User
from bitlipa.apps.roles.models import Role
from bitlipa.apps.roles.serializers import RoleSerializer


class UserRole(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, null=True)

    objects = UserRoleManager()

    class Meta:
        db_table = "user_roles"
        ordering = ("user_id", "role_id")
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'role_id'], name='unique_user_role')
        ]

    def get_role(self):
        return RoleSerializer(self.role).data

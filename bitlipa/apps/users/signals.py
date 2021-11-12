from django.db.models.signals import post_save, pre_delete
from bitlipa.apps.users.models import User
from bitlipa.apps.user_activity.models import UserActivity
from django.dispatch import receiver



@receiver(post_save, sender=User)
def create_activity(sender, instance, created, **kwargs):
    if created:
        creator = User.objects.get(id=instance.creator_id)
        description = f'{creator.first_name} {creator.last_name} created {instance.first_name} {instance.last_name}'

        user = UserActivity(title='create admin', description=description, user_id=instance.creator_id)
        user.save()


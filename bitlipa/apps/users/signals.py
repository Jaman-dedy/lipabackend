from django.db.models.signals import post_save
from bitlipa.apps.users.models import User
from bitlipa.apps.user_activity.models import UserActivity
from django.dispatch import receiver


@receiver(post_save, sender=User)
def post_save_handler(sender, instance, created, **kwargs):
    if created:
        try:
            creator = User.objects.get(id=instance.creator_id)
            description = f'{creator.first_name} {creator.last_name} created {instance.first_name} {instance.last_name}'
            activity = UserActivity(title='account creation', description=description, user_id=instance.creator_id)
        except User.DoesNotExist:
            description = f'{instance.first_name} {instance.last_name} created an account'
            activity = UserActivity(title='account creation', description=description, user_id=instance.id)

        activity.save()

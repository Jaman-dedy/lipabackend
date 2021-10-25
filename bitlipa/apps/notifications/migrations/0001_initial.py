# Generated by Django 3.2.4 on 2021-10-25 06:46

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0015_user_is_password_temporary'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=30, null=True, verbose_name='title')),
                ('content', models.CharField(blank=True, max_length=255, null=True, verbose_name='content')),
                ('delivery_option', models.CharField(blank=True, max_length=30, null=True, verbose_name='delivery_mode')),
                ('image_url', models.CharField(blank=True, max_length=255, null=True, verbose_name='image')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('deleted_at', models.DateTimeField(null=True, verbose_name='deleted at')),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='users.user')),
            ],
            options={
                'db_table': 'notifications',
                'ordering': ('sender', 'title', 'content', 'delivery_option'),
            },
        ),
    ]

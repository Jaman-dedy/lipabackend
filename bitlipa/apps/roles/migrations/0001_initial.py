# Generated by Django 3.2.4 on 2021-10-04 19:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=30, null=True, verbose_name='tile')),
                ('description', models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='description')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('deleted_at', models.DateTimeField(null=True, verbose_name='deleted at')),
            ],
            options={
                'db_table': 'role',
                'ordering': ('title', 'description'),
            },
        ),
    ]
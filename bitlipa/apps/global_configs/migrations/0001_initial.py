# Generated by Django 3.2.4 on 2021-12-22 00:03

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalConfig',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30, verbose_name='name')),
                ('_data', models.TextField(blank=True, null=True, verbose_name='data')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('deleted_at', models.DateTimeField(null=True, verbose_name='deleted at')),
            ],
            options={
                'db_table': 'global_configs',
                'ordering': ('created_at', 'updated_at'),
            },
        ),
        migrations.AddConstraint(
            model_name='globalconfig',
            constraint=models.UniqueConstraint(fields=('name',), name='unique_global_config'),
        ),
    ]

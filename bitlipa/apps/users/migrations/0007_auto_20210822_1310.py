# Generated by Django 3.2.4 on 2021-08-22 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_user_firebase_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='country',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='country'),
        ),
        migrations.AddField(
            model_name='user',
            name='country_code',
            field=models.CharField(blank=True, max_length=6, null=True, verbose_name='country code'),
        ),
    ]

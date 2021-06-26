# Generated by Django 3.2.4 on 2021-06-16 19:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FiatWallet',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('wallet_name', models.CharField(blank=True, max_length=30, null=True, verbose_name='wallet name')),
                ('wallet_number', models.CharField(blank=True, max_length=30, null=True, verbose_name='wallet number')),
                ('wallet_currency', models.CharField(blank=True, max_length=30, null=True, verbose_name='wallet currency')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('deleted_at', models.DateTimeField(auto_now=True, verbose_name='deleted at')),
            ],
            options={
                'db_table': 'fiat_wallet',
                'ordering': ('wallet_name', 'wallet_number', 'wallet_currency'),
            },
        )
    ]

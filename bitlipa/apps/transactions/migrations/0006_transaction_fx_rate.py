# Generated by Django 3.2.4 on 2021-11-12 18:03

from decimal import Decimal
from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0005_auto_20211112_1801'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='fx_rate',
            field=djmoney.models.fields.MoneyField(currency_field_name='target_currency', decimal_places=18, default=Decimal('0'), max_digits=36, verbose_name='currency exchange rate'),
        ),
    ]
# Generated by Django 3.2.4 on 2022-04-24 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20211231_0233'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='daily_tx_total_amount',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=19, null=True, verbose_name='total amount of daily transactions'),
        ),
        migrations.AddField(
            model_name='user',
            name='monthly_tx_total_amount',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=19, null=True, verbose_name='total amount of monthly transactions'),
        ),
        migrations.AddField(
            model_name='user',
            name='weekly_tx_total_amount',
            field=models.DecimalField(blank=True, decimal_places=4, default=0, max_digits=19, null=True, verbose_name='total amount of weekly transactions'),
        ),
    ]
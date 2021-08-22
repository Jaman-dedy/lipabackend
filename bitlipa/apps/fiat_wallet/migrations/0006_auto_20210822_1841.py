# Generated by Django 3.2.4 on 2021-08-22 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fiat_wallet', '0005_auto_20210822_1622'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fiatwallet',
            options={'ordering': ('name', 'currency', 'number')},
        ),
        migrations.AddField(
            model_name='fiatwallet',
            name='number',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='wallet number'),
        ),
    ]
# Generated by Django 3.2.4 on 2021-08-22 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fiat_wallet', '0003_alter_fiatwallet_wallet_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fiatwallet',
            options={'ordering': ('name', 'currency', 'currency')},
        ),
        migrations.RenameField(
            model_name='fiatwallet',
            old_name='wallet_currency',
            new_name='currency',
        ),
        migrations.RenameField(
            model_name='fiatwallet',
            old_name='wallet_name',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='fiatwallet',
            name='wallet_number',
        ),
    ]
# Generated by Django 3.2.4 on 2021-12-19 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_auto_20211218_2218'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='status',
            field=models.CharField(choices=[('SEEN', 'Seen'), ('UNSEEN', 'Unseen')], default='UNSEEN', max_length=6, verbose_name='read status'),
        ),
    ]

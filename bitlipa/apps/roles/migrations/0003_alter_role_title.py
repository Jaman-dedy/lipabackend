# Generated by Django 3.2.4 on 2021-11-12 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roles', '0002_alter_role_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='title',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='title'),
        ),
    ]

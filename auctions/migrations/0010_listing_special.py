# Generated by Django 3.2.9 on 2022-01-04 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_auto_20220104_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='special',
            field=models.BooleanField(default=False),
        ),
    ]

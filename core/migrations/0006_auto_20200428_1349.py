# Generated by Django 2.2 on 2020-04-28 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20200428_1348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='room_number',
            field=models.IntegerField(),
        ),
    ]

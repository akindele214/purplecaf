# Generated by Django 2.2 on 2020-04-28 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20200428_1308'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='block_number',
            field=models.CharField(default=14, max_length=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='address',
            name='room_number',
            field=models.IntegerField(default=2, max_length=3),
            preserve_default=False,
        ),
    ]

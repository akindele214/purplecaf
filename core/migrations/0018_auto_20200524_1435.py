# Generated by Django 2.2 on 2020-05-24 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20200524_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voucheraccount',
            name='amount',
            field=models.IntegerField(default=0),
        ),
    ]
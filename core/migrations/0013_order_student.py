# Generated by Django 2.2 on 2020-05-07 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20200506_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='student',
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
    ]

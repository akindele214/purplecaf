# Generated by Django 2.2 on 2020-04-27 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20200427_1246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('RI', 'Rice'), ('CH', 'Chips'), ('DR', 'Drinks'), ('PA', 'Pap'), ('BR', 'Bread'), ('BI', 'Biscuit')], max_length=2),
        ),
    ]

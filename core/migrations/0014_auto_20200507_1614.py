# Generated by Django 2.2 on 2020-05-07 14:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_order_student'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='student',
            new_name='student_number',
        ),
    ]

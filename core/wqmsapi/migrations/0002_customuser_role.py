# Generated by Django 4.2.13 on 2024-06-06 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_wqmsapi', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('user', 'User')], default='user', max_length=10),
        ),
    ]

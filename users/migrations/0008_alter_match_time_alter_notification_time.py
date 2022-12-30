# Generated by Django 4.1.4 on 2022-12-30 01:35

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0007_alter_notification_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="match",
            name="time",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="notification",
            name="time",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

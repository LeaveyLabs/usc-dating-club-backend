# Generated by Django 4.1.6 on 2023-02-12 22:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0038_message_timestamp"),
    ]

    operations = [
        migrations.RemoveField(model_name="message", name="datetime",),
    ]

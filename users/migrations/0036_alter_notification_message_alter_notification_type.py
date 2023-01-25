# Generated by Django 4.1.4 on 2023-01-25 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0035_alter_notification_message_message"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="message",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="notification",
            name="type",
            field=models.CharField(
                choices=[("match", "match"), ("accept", "accept"), ("stop", "stop")],
                max_length=15,
            ),
        ),
    ]
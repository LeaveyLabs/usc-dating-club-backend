# Generated by Django 4.1.4 on 2023-01-25 06:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0034_alter_basequestion_header_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="message",
            field=models.TextField(default=""),
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("body", models.TextField()),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "receiver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="received_messages",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sent_messages",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

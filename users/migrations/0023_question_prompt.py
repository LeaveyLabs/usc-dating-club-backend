# Generated by Django 4.1.4 on 2023-01-15 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0022_bannedemail_waitingemail"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="prompt",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
    ]

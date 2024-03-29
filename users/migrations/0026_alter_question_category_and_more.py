# Generated by Django 4.1.4 on 2023-01-17 01:49

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0025_alter_question_category_alter_question_header"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="category",
            field=models.TextField(
                choices=[
                    ("organized/chaotic", "organized/chaotic"),
                    ("extraverted/introverted", "extraverted/introverted"),
                    ("sentimental/stoic", "sentimental/stoic"),
                    ("empathetic/intellectual", "empathetic/intellectual"),
                    ("bold/patient", "bold/patient"),
                    ("spontaneous/intentional", "spontaneous/intentional"),
                    ("timely/flexible", "timely/flexible"),
                    ("agreeable/strong-willed", "agreeable/strong-willed"),
                    (
                        "family-oriented/career-oriented",
                        "family-oriented/career-oriented",
                    ),
                    ("frugal/bougie", "frugal/bougie"),
                    ("dog-lover/cat-lover", "dog-lover/cat-lover"),
                    ("academic/artistic", "academic/artistic"),
                    ("minimalistic/materialistic", "minimalistic/materialistic"),
                    ("self-aware/blissfully-unaware", "self-aware/blissfully-unaware"),
                    ("prudent/yolo", "prudent/yolo"),
                    ("laid-back/straightedge", "laid-back/straightedge"),
                    ("attentive/idgaf", "attentive/idgaf"),
                    ("early-bird/night-owl", "early-bird/night-owl"),
                    ("open-minded/disciplined", "open-minded/disciplined"),
                    ("languages", "languages"),
                    ("love-languages", "love-languages"),
                    ("politics", "politics"),
                    ("religion", "religion"),
                    ("diet", "diet"),
                    ("drugs", "drugs"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="text_answer_choices",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(), blank=True, default=list, size=None
            ),
        ),
    ]

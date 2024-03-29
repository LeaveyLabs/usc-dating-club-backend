# Generated by Django 4.1.4 on 2023-01-21 20:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0033_rename_question_numericalquestion_base_question_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="basequestion",
            name="header",
            field=models.TextField(
                choices=[
                    ("personality", "personality"),
                    ("preferences", "preferences"),
                    ("values", "values"),
                    ("lifestyle", "lifestyle"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="numericalquestion",
            name="base_question",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="numerical_question",
                to="users.basequestion",
            ),
        ),
        migrations.AlterField(
            model_name="textquestion",
            name="base_question",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="text_question",
                to="users.basequestion",
            ),
        ),
    ]

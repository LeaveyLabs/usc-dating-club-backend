# Generated by Django 4.1.4 on 2023-01-21 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0028_remove_question_avg_remove_question_std_dev_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="question", name="maximum", field=models.FloatField(default=6),
        ),
        migrations.AddField(
            model_name="question", name="minimum", field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="question", name="average", field=models.FloatField(default=3),
        ),
    ]
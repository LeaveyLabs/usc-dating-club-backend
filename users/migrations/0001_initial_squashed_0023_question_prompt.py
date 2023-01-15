# Generated by Django 4.1.4 on 2023-01-15 17:09

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields
import users.models


class Migration(migrations.Migration):

    replaces = [
        ("users", "0001_initial"),
        ("users", "0002_remove_user_picture"),
        ("users", "0003_remove_user_date_of_birth"),
        ("users", "0004_user_latitude_user_longitude_and_more"),
        ("users", "0005_alter_emailauthentication_email_and_more"),
        ("users", "0006_notification_match"),
        ("users", "0007_alter_notification_type"),
        ("users", "0008_alter_match_time_alter_notification_time"),
        ("users", "0009_alter_user_sex_identity_alter_user_sex_preference"),
        ("users", "0010_alter_user_latitude_alter_user_longitude"),
        ("users", "0011_user_loc_update_time"),
        ("users", "0012_alter_user_sex_identity_alter_user_sex_preference"),
        ("users", "0013_rename_type_question_category"),
        ("users", "0014_notification_sound"),
        ("users", "0015_user_is_matchable_alter_question_user"),
        ("users", "0016_match_accept_notification_sent_and_more"),
        ("users", "0017_remove_question_answer_remove_question_user_and_more"),
        ("users", "0018_question_is_numerical"),
        ("users", "0019_question_is_multiple_answer"),
        ("users", "0020_question_text_answer_choices"),
        ("users", "0021_alter_question_text_answer_choices"),
        ("users", "0022_bannedemail_waitingemail"),
        ("users", "0023_question_prompt"),
    ]

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=128, region=None, unique=True
                    ),
                ),
                (
                    "sex_identity",
                    models.TextField(
                        choices=[("m", "MALE"), ("f", "FEMALE"), ("b", "BOTH")]
                    ),
                ),
                (
                    "sex_preference",
                    models.TextField(
                        choices=[("m", "MALE"), ("f", "FEMALE"), ("b", "BOTH")]
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("longitude", models.FloatField(blank=True, null=True)),
                (
                    "loc_update_time",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("is_matchable", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[("objects", django.contrib.auth.models.UserManager()),],
        ),
        migrations.CreateModel(
            name="EmailAuthentication",
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
                ("email", models.EmailField(max_length=254)),
                ("code", models.TextField(default=users.models.random_code)),
                ("is_verified", models.BooleanField(default=False)),
                ("proxy_uuid", models.UUIDField()),
            ],
        ),
        migrations.CreateModel(
            name="PhoneAuthentication",
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
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=128, region=None
                    ),
                ),
                ("code", models.TextField(default=users.models.random_code)),
                ("is_verified", models.BooleanField(default=False)),
                ("proxy_uuid", models.UUIDField()),
            ],
        ),
        migrations.CreateModel(
            name="Match",
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
                ("time", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "user1",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="match1",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user2",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="match2",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("accept_notification_sent", models.BooleanField(default=False)),
                ("initial_notification_sent", models.BooleanField(default=False)),
                ("user1_accepted", models.BooleanField(default=False)),
                ("user2_accepted", models.BooleanField(default=False)),
            ],
            options={"unique_together": {("user1", "user2")},},
        ),
        migrations.CreateModel(
            name="Notification",
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
                (
                    "type",
                    models.CharField(
                        choices=[("match", "match"), ("accept", "accept")],
                        max_length=15,
                    ),
                ),
                ("message", models.TextField()),
                ("data", models.JSONField(blank=True, null=True)),
                ("time", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("sound", models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Question",
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
                (
                    "category",
                    models.TextField(choices=[(0, "What time do you sleep at night?")]),
                ),
                ("is_numerical", models.BooleanField(default=False)),
                ("is_multiple_answer", models.BooleanField(default=False)),
                (
                    "text_answer_choices",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.TextField(), default=list, size=None
                    ),
                ),
                ("prompt", models.TextField(default="")),
            ],
        ),
        migrations.CreateModel(
            name="TextResponse",
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
                ("answer", models.TextField()),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="text_responses",
                        to="users.question",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="text_responses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="NumericalResponse",
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
                ("answer", models.FloatField()),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="numerical_responses",
                        to="users.question",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="numerical_responses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BannedEmail",
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
                ("email", models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name="WaitingEmail",
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
                ("email", models.EmailField(max_length=254)),
            ],
        ),
    ]
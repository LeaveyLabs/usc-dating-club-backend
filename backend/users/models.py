""" Defines database models for Users """
import os
import random
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

def profile_picture_filepath(instance, filename) -> str:
    """ Returns save location of profile picture """
    ext = filename.split('.')[-1]
    new_filename = f'{instance.username}.{ext}'
    return os.path.join('profiles', new_filename)

def random_code() -> str:
    """ Returns a six-digit random code """
    return "".join([str(random.randint(0, 9)) for _ in range(6)])

class User(AbstractUser):
    """ User class extension """

    SEX_CHOICES = (
      (0, 'MALE'),
      (1, 'FEMALE'),
      (2, 'BOTH'),
      (3, 'OTHER'),
    )

    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(unique=True)
    sex_identity = models.TextField(choices=SEX_CHOICES)
    sex_preference = models.TextField(choices=SEX_CHOICES)

    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    def save(self, *args, **kwargs) -> None:
        """ Overrides username and password generation """
        self.username = uuid4()
        self.password = uuid4()
        return super().save(*args, **kwargs)

class Question(models.Model):
    """ Compatibility questions for matching users """

    QUESTION_CHOICES = (
      (0,  'What time do you sleep at night?'),
    )

    type = models.TextField(choices=QUESTION_CHOICES)
    answer = models.IntegerField()

    user = models.ForeignKey(User, on_delete=models.CASCADE)

class EmailAuthentication(models.Model):
    """ Authenticate email with verification code """
    email = models.EmailField()
    code = models.TextField(default=random_code)
    is_verified = models.BooleanField(default=False)
    proxy_uuid = models.UUIDField()

class PhoneAuthentication(models.Model):
    """ Authenticate phone with verificiation code """
    phone_number = PhoneNumberField()
    code = models.TextField(default=random_code)
    is_verified = models.BooleanField(default=False)
    proxy_uuid = models.UUIDField()
    
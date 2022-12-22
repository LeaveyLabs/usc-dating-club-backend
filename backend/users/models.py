""" Imports """
import os

from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

def profile_picture_filepath(instance, filename) -> str:
    """ Returns save location of profile picture """
    ext = filename.split('.')[-1]
    new_filename = f'{instance.username}.{ext}'
    return os.path.join('profiles', new_filename)

class User(AbstractUser):
    """ User class extension """

    class SexChoices(models.IntegerChoices):
        """ Enum for questions options. """
        SLEEP = 0, 'What time do you sleep at night?'

    email = models.EmailField()
    date_of_birth = models.DateField()
    picture = models.ImageField(upload_to=profile_picture_filepath)
    phone_number = PhoneNumberField()
    sex = 

class Question(models.Model):
    """ Compatibility questions for matching users. """

    class QuestionChoices(models.IntegerChoices):
        """ Enum for questions options. """
        SLEEP = 0, 'What time do you sleep at night?'

    type = models.TextField(choices=QuestionChoices)
    answer = models.IntegerField()

    user = models.ForeignKey(User, on_delete=models.CASCADE)

""" Defines database models for Users """
import os
import random
from uuid import uuid4

from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from push_notifications.models import APNSDevice

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

    class SexChoices:
        MALE = 'm'
        FEMALE = 'f'
        BOTH = 'b'

    SEX_CHOICES = (
      (SexChoices.MALE, 'MALE'),
      (SexChoices.FEMALE, 'FEMALE'),
      (SexChoices.BOTH, 'BOTH'),
    )

    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(unique=True)
    sex_identity = models.TextField(choices=SEX_CHOICES)
    sex_preference = models.TextField(choices=SEX_CHOICES)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    loc_update_time = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs) -> None:
        """ Overrides username and password generation """
        self.username = self.email
        self.password = self.password if self.password else uuid4()
        return super().save(*args, **kwargs)

class Match(models.Model):
    """ Match between two users """
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match2")
    time = models.DateTimeField(default=timezone.now)

    MATCH_SOUND = "matchsound.wav"

    class Meta:
        """ Two users cannot match more than once """
        unique_together = ('user1', 'user2', )

    def save(self, *args, **kwargs) -> None:
        """ Order the users and notify each of them """
        self.user1, self.user2 = sorted([self.user1, self.user2], key=lambda user: user.email)
        super().save(*args, **kwargs)
        self.send_notifications()
    
    def has_expired(self):
        return timezone.now() - self.time > timedelta(days=2)
    
    def send_notifications(self):
        Notification.objects.bulk_create([
          Notification(
            user=self.user1,
            type=Notification.Choices.MATCH,
            message=self.match_message(self.user1.first_name, self.user2.first_name),
            data=self.notifcation_payload(self.user1, self.user2),
            sound=self.MATCH_SOUND,
          ),
          Notification(
            user=self.user2,
            type=Notification.Choices.MATCH,
            message=self.match_message(self.user2.first_name, self.user1.first_name),
            data=self.notifcation_payload(self.user1, self.user2),
            sound=self.MATCH_SOUND,
          ),
        ])

    def match_message(self, receiver_name, sender_name) -> str:
        return f'{receiver_name}, you matched with {sender_name}!'

    def notifcation_payload(self, user1, user2):
        return {
            'user1_id': user1.id,
            'user2_id': user2.id,
        }
    

class Question(models.Model):
    """ Compatibility questions for matching users """

    QUESTION_CHOICES = (
      (0,  'What time do you sleep at night?'),
    )

    category = models.TextField(choices=QUESTION_CHOICES)
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

class NotificationManager(models.Manager):
    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        notifications = super().bulk_create(objs, batch_size, ignore_conflicts)
        for notification in notifications:
            notification.send_to_device()
        return notifications

class Notification(models.Model):
    """ Wrapper for APNS Notifications """
    class Choices:
        MATCH = "match"
    
    NOTIFICATION_OPTIONS = (
        (Choices.MATCH, Choices.MATCH),
    )

    objects = NotificationManager()

    user = models.ForeignKey(User, related_name="notifications", on_delete=models.CASCADE)
    type = models.CharField(max_length=15, choices=NOTIFICATION_OPTIONS,)
    message = models.TextField()
    data = models.JSONField(null=True, blank=True)
    time = models.DateTimeField(default=timezone.now)
    sound = models.TextField(null=True)

    def send_to_device(self) -> None:
        APNSDevice.objects.filter(user=self.user).send_message(
            self.message,
            extra={
                "type": self.type,
                "data": self.data,
                "sound": self.sound
            }
        )
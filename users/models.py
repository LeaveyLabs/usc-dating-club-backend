""" Defines database models for Users """
import os
import random
from uuid import uuid4

from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from math import radians, cos, sin, asin, sqrt
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

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    if not lon1 or not lat1 or not lon2 or not lat2: 
        return None
    
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r

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
    is_matchable = models.BooleanField(default=False)

    def save(self, *args, **kwargs) -> None:
        """ Overrides username and password generation """
        self.username = self.email
        self.password = self.password if self.password else uuid4()
        self.first_name = self.first_name.lower()
        self.last_name = self.last_name.lower()
        return super().save(*args, **kwargs)

class Match(models.Model):
    """ Match between two users """
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match2")
    user1_accepted = models.BooleanField(default=False)
    user2_accepted = models.BooleanField(default=False)
    initial_notification_sent = models.BooleanField(default=False)
    accept_notification_sent = models.BooleanField(default=False)
    time = models.DateTimeField(default=timezone.now)

    MATCH_SOUND = "matchsound.wav"

    class Meta:
        """ Two users cannot match more than once """
        unique_together = ('user1', 'user2', )

    def save(self, *args, **kwargs) -> None:
        """ Order the users and notify each of them """
        self.user1, self.user2 = sorted([self.user1, self.user2], key=lambda user: user.email)

        if not self.initial_notification_sent:
            self.send_initial_match_notifications()
            self.initial_notification_sent = True

        if (not self.accept_notification_sent
            and self.user1_accepted
            and self.user2_accepted):
            self.send_accept_match_notifications()
            self.accept_notification_sent = True

        super().save(*args, **kwargs)
    
    def has_expired(self) -> bool:
        return (timezone.now() - self.time) > timedelta(days=2)
    
    def send_initial_match_notifications(self) -> None:
        """ Notifies users that they've been matched """
        Notification.objects.bulk_create([
          Notification(
            user=self.user1,
            type=Notification.Choices.MATCH,
            message=self.match_message(self.user1.first_name, self.user2.first_name),
            data=self.initial_match_payload(self.user2, self.user1),
            sound=self.MATCH_SOUND,
          ),
          Notification(
            user=self.user2,
            type=Notification.Choices.MATCH,
            message=self.match_message(self.user2.first_name, self.user1.first_name),
            data=self.initial_match_payload(self.user1, self.user2),
            sound=self.MATCH_SOUND,
          ),
        ])
    
    def send_accept_match_notifications(self) -> None:
        """ Notifies users that their match was accepted """
        Notification.objects.bulk_create([
          Notification(
            user=self.user1,
            type=Notification.Choices.ACCEPT,
            data=self.accept_match_payload(self.user2, self.user1),
          ),
          Notification(
            user=self.user2,
            type=Notification.Choices.ACCEPT,
            data=self.accept_match_payload(self.user1, self.user2),
          ),
        ])

    def match_message(self, receiver_name, sender_name) -> str:
        return f'{receiver_name}, you matched with {sender_name}!'

    def initial_match_payload(self, user, partner) -> dict:
        return {
            'id': partner.id,
            'first_name': partner.first_name,
            'email': partner.email,
            'time': timezone.now().timestamp(),
            'compatibility': random.randint(90, 99),
            'distance': haversine(
                user.longitude,
                user.latitude,
                partner.longitude,
                partner.latitude),
        }

    def accept_match_payload(self, user, partner) -> dict:
        return {
            'id': partner.id,
            'first_name': partner.first_name,
            'email': partner.email,
            'time': timezone.now().timestamp(),
            'compatibility': random.randint(90, 99),
            'distance': haversine(
                user.longitude,
                user.latitude,
                partner.longitude,
                partner.latitude),
        }
    

class Question(models.Model):
    """ Compatibility questions for matching users """

    QUESTION_CHOICES = (
      (0,  'What time do you sleep at night?'),
    )

    category = models.TextField(choices=QUESTION_CHOICES)
    is_numerical = models.BooleanField(default=False)
    is_multiple_answer = models.BooleanField(default=False)

class NumericalResponse(models.Model):
    question = models.ForeignKey(Question, related_name="numerical_responses", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="numerical_responses", on_delete=models.CASCADE)
    answer = models.FloatField()

class TextResponse(models.Model):
    question = models.ForeignKey(Question, related_name="text_responses", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="text_responses", on_delete=models.CASCADE)
    answer = models.TextField()

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
        ACCEPT = "accept"
    
    NOTIFICATION_OPTIONS = (
        (Choices.MATCH, Choices.MATCH),
        (Choices.ACCEPT, Choices.ACCEPT),
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
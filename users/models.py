""" Defines database models for Users """
import copy
import os
import random
from uuid import uuid4

from datetime import datetime, timedelta
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from mp_config import MixpanelClient
from math import radians, cos, sin, asin, sqrt
from phonenumber_field.modelfields import PhoneNumberField
from push_notifications.models import APNSDevice
from rest_framework.authtoken.models import Token

def profile_picture_filepath(instance, filename) -> str:
    """ Returns save location of profile picture """
    ext = filename.split('.')[-1]
    new_filename = f'{instance.username}.{ext}'
    return os.path.join('profiles', new_filename)

def random_code() -> str:
    """ Returns a six-digit random code """
    return "".join([str(random.randint(0, 9)) for _ in range(6)])

def current_timestamp() -> float:
    """ Returns the timestamp in the current timezone """
    return timezone.now().timestamp()

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in meters between two points 
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
    return c * r * 1000

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

    def picture_filepath(instance, filename):
        ext = filename.split('.')[-1]
        new_filename = f'{instance.username}.{ext}'
        return os.path.join('profiles', new_filename)

    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(unique=True)
    sex_identity = models.TextField(choices=SEX_CHOICES)
    sex_preference = models.TextField(choices=SEX_CHOICES)
    picture = models.ImageField(upload_to=picture_filepath, null=True, blank=True)

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
        user = super().save(*args, **kwargs)
        if not Token.objects.filter(user_id=self.id).exists():
            Token.objects.create(user_id=self.id)
        return user

class Interest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="interest")
    category = models.TextField()

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

    def save(self, setting_notification=False, *args, **kwargs) -> None:
        """ Order the users and notify each of them """
        super().save(*args, **kwargs)

        if setting_notification: return

        self.user1, self.user2 = sorted([self.user1, self.user2], key=lambda user: user.email)

        if not self.initial_notification_sent:
            self.send_initial_match_notifications()
            self.initial_notification_sent = True
            self.save(setting_notification=True)

        if (not self.accept_notification_sent
            and self.user1_accepted
            and self.user2_accepted):
            self.send_accept_match_notifications()
            self.accept_notification_sent = True
            self.save(setting_notification=True)

    def has_expired(self) -> bool:
        return (timezone.now() - self.time) > timedelta(days=1)

    def send_match_create_to_mixpanel(self, payload1, payload2, compatibility) -> None:
        MixpanelClient.track(self.user1.id, 'Match Create', {
            'match_id': self.id,
            'numerical_traits': [
                similarity['trait'] 
                for similarity in payload1['numerical_similarities']
            ],
            'text_traits': [
                similarity['trait'] 
                for similarity in payload1['text_similarities']
            ],
            'compatibility': compatibility,
            'latitude': payload1['latitude'],
            'longitude': payload1['longitude'],
            'distance': payload1['distance'],
        })
        
        MixpanelClient.track(self.user2.id, 'Match Create', {
            'match_id': self.id,
            'numerical_traits': [
                similarity['trait'] 
                for similarity in payload1['numerical_similarities']
            ],
            'text_traits': [
                similarity['trait'] 
                for similarity in payload1['text_similarities']
            ],
            'compatibility': compatibility,
            'latitude': payload2['latitude'],
            'longitude': payload2['longitude'],
            'distance': payload1['distance'],
        })

    def send_match_accept_to_mixpanel(self) -> None:
        MixpanelClient.track(self.user1.id, 'Match Success')
        MixpanelClient.track(self.user2.id, 'Match Success')
    
    def send_initial_match_notifications(self) -> None:
        """ Notifies users that they've been matched """
        payload1 = self.initial_match_payload(self.user2, self.user1)
        payload2 = self.flip_match_payload(self.user1, payload1)

        compatibility = payload1['compatibility']

        Notification.objects.bulk_create([
          Notification(
            user=self.user1,
            type=Notification.Choices.MATCH,
            message=self.match_message(self.user2.first_name, compatibility),
            data=payload1,
            sound=self.MATCH_SOUND,
          ),
          Notification(
            user=self.user2,
            type=Notification.Choices.MATCH,
            message=self.match_message(self.user1.first_name, compatibility),
            data=payload2,
            sound=self.MATCH_SOUND,
          ),
        ])

        self.send_match_create_to_mixpanel(payload1, payload2, compatibility)
    
    def send_accept_match_notifications(self) -> None:
        """ Notifies users that their match was accepted """
        payload1 = self.initial_match_payload(self.user2, self.user1)
        payload2 = self.initial_match_payload(self.user1, self.user2)
        
        Notification.objects.bulk_create([
          Notification(
            user=self.user1,
            message=self.accept_message(self.user2.first_name),
            type=Notification.Choices.ACCEPT,
            data=payload1,
          ),
          Notification(
            user=self.user2,
            message=self.accept_message(self.user1.first_name),
            type=Notification.Choices.ACCEPT,
            data=payload2,
          ),
        ])

        self.send_match_accept_to_mixpanel()

    def match_message(self, sender_name, comptability) -> str:
        return f'{sender_name} is nearby and {comptability}% compatible with you. you have 5 minutes to respond'

    def accept_message(self, sender_name) -> str:
        return f'{sender_name} is down to meet up. you have 5 minutes to go and say hi'

    def flip_match_payload(self, partner, payload) -> dict:
        payload_copy = copy.deepcopy(payload)

        payload_copy['id'] = partner.id
        payload_copy['first_name'] = partner.first_name
        payload_copy['email'] = partner.email

        numerical_similarities = payload.get('numerical_similarities')
        for i, similarity in enumerate(numerical_similarities):
            you = similarity.get('you_percent')
            partner = similarity.get('partner_percent')
            payload_copy['numerical_similarities'][i]['you_percent'] = partner
            payload_copy['numerical_similarities'][i]['partner_percent'] = you
        
        return payload_copy

    def is_excluded_response(self, response) -> bool:
        return response in ["none/other", "other", "none"]

    def initial_match_payload(self, partner, user) -> dict:
        try:
            user.numerical_responses
            user.text_responses
        except:
            user.numerical_responses = NumericalResponse.objects.filter(user=user)
            user.text_responses = TextResponse.objects.filter(user=user)
        
        compatible_numerical_responses = Q()
        for response in user.numerical_responses.all():
            compatible_numerical_responses |= (
              (
                Q(question_id=response.question_id)&
                Q(question__average__lte=response.answer)&
                Q(answer__lte=response.answer)
              ) | (
                Q(question_id=response.question_id)&
                Q(question__average__gte=response.answer)&
                Q(answer__gte=response.answer)
              )
            )
        
        compatible_text_responses = Q()
        for response in user.text_responses.all():
            compatible_text_responses |= (
              Q(question_id=response.question_id)&
              Q(answer=response.answer)
            )
        
        similar_numerical_responses = NumericalResponse.objects.filter(
           Q(user=partner)&
           compatible_numerical_responses
        )
        similar_text_responses = TextResponse.objects.filter(
           Q(user=partner)&
           compatible_text_responses
        )

        serialized_numerical_similarities = []
        serialized_text_similarities = []

        similar_traits = set()

        for response in similar_numerical_responses.all():
            category = response.question.base_question.category
            if not category: continue
            if not category.trait1 or not category.trait2: continue

            below_average = response.answer < response.question.average
            trait = category.trait1 if below_average else category.trait2

            if trait in similar_traits: continue
            similar_traits.add(trait)

            you_percent = random.randint(85, 99)
            partner_percent = random.randint(85, 99)
            if partner_percent == you_percent:
                partner_percent += 2

            serialized_numerical_similarities.append({
                'trait': trait,
                'avg_percent': random.randint(35, 65),
                'you_percent': you_percent,
                'partner_percent': partner_percent,
            })

        for response in similar_text_responses.all():
            category = response.question.base_question.category

            if self.is_excluded_response(response.answer): continue

            if not category: continue
            trait = response.question.base_question.category.trait1

            if trait in similar_traits: continue
            similar_traits.add(trait)

            answer_choices = TextAnswerChoice.objects.filter(
                question_id=response.question.id,
                answer=response.answer,
            )
            emoji = answer_choices[0].emoji if answer_choices.exists() else '❤️'
            serialized_text_similarities.append({
                'trait': trait,
                'shared_response': response.answer,
                'emoji': emoji,
            })

        serialized_numerical_similarities = self.prune_identical_similarities(
            serialized_numerical_similarities
        )
        serialized_text_similarities = self.prune_identical_similarities(
            serialized_text_similarities
        )

        if len(serialized_numerical_similarities) < 3:
            serialized_numerical_similarities = self.default_numerical_similarities()
            # num_needed_defaults = 3 - len(serialized_numerical_similarities)
            # defaults = self.default_numerical_similarities()
            # serialized_numerical_similarities += defaults[:num_needed_defaults]
        
        serialized_numerical_similarities = random.sample(
            serialized_numerical_similarities, k=3,
        )

        if len(serialized_text_similarities) > 3:
            serialized_text_similarities = random.sample(
                serialized_text_similarities, k=3,
            )

        return {
            'match_id': self.id,
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
            'latitude': partner.latitude,
            'longitude': partner.longitude,
            'numerical_similarities': serialized_numerical_similarities,
            'text_similarities': serialized_text_similarities,
        }

    def accept_match_payload(self, user, partner) -> dict:
        return {
            'match_id': self.id,
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
            'latitude': partner.latitude,
            'longitude': partner.longitude,
        }

    def prune_identical_similarities(self, similarities):
        pruned_similarities = []
        seen_traits = set()
        for similarity in similarities:
            if similarity.get('trait') in seen_traits:
                continue
            seen_traits.add(similarity.get('trait'))
            pruned_similarities.append(similarity)
        return pruned_similarities

    def default_numerical_similarities(self):
        traits = ['open-minded', 'intentional', 'empathetic']
        random_percents = [random.randint(85, 99) for _ in range(len(traits)*2)]
        random_averages = [random.randint(35, 65) for _ in range(len(traits))]
        defaults = []
        for i, trait in enumerate(traits):
            p_i = 2*i
            defaults.append({
                'trait': trait,
                'avg_percent': random_averages[i],
                'you_percent': random_percents[p_i+1],
                'partner_percent': random_percents[p_i],
            })

        return defaults
    

class Category(models.Model):
    trait1 = models.TextField()
    trait2 = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return str(self.trait1)

class BaseQuestion(models.Model):
    """ Compatibility questions for matching users """

    """ Headers to display the questions """
    HEADER_OPTIONS = (
        "personality",
        "preferences",
        "values",
        "lifestyle",
    )

    HEADER_TUPLES = (
        (header, header) for header in HEADER_OPTIONS
    )

    header = models.TextField(choices=HEADER_TUPLES)
    category = models.ForeignKey(
        Category,
        related_name='questions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    prompt = models.TextField()

class NumericalQuestion(models.Model):
    base_question = models.OneToOneField(BaseQuestion, related_name="numerical_question", on_delete=models.CASCADE)
    average = models.FloatField(default=3)
    variance = models.FloatField(default=1)
    minimum = models.FloatField(default=0)
    maximum = models.FloatField(default=6)

    def __str__(self):
        return str(self.base_question.prompt) 

    def calculate_average(self):
        numerical_responses = self.numerical_responses.all()
        return sum([response.answer for response in numerical_responses])/len(numerical_responses)

class TextQuestion(models.Model):
    base_question = models.OneToOneField(BaseQuestion, related_name="text_question", on_delete=models.CASCADE)
    is_multiple_answer = models.BooleanField(default=False)

    def __str__(self):
        return str(self.base_question.prompt)

class TextAnswerChoice(models.Model):
    emoji = models.TextField()
    answer = models.TextField()
    question = models.ForeignKey(TextQuestion, related_name="text_answer_choices", on_delete=models.CASCADE)

class NumericalResponse(models.Model):
    question = models.ForeignKey(NumericalQuestion, related_name="numerical_responses", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="numerical_responses", on_delete=models.CASCADE)
    answer = models.FloatField()

    def save(self, *args, **kwargs):
        NumericalResponse.objects.filter(
            question=self.question,
            user=self.user,
        ).delete()
        super().save(*args, **kwargs)
        # self.question.calculate_average()
        # self.question.save()

class TextResponse(models.Model):
    question = models.ForeignKey(TextQuestion, related_name="text_responses", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="text_responses", on_delete=models.CASCADE)
    answer = models.TextField()

    def save(self, *args, **kwargs):
        TextResponse.objects.filter(
            question=self.question,
            user=self.user,
        ).delete()
        super().save(*args, **kwargs)

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

class WaitingEmail(models.Model):
    """ Email on waiting list """
    email = models.EmailField()

class BannedEmail(models.Model):
    """ Email on banned list """
    email = models.EmailField()

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
        STOP_SHARE = "stop"
    
    NOTIFICATION_OPTIONS = (
        (Choices.MATCH, Choices.MATCH),
        (Choices.ACCEPT, Choices.ACCEPT),
        (Choices.STOP_SHARE, Choices.STOP_SHARE),
    )

    objects = NotificationManager()

    user = models.ForeignKey(User, related_name="notifications", on_delete=models.CASCADE)
    type = models.CharField(max_length=15, choices=NOTIFICATION_OPTIONS,)
    message = models.TextField(null=True, blank=True)
    data = models.JSONField(null=True, blank=True)
    time = models.DateTimeField(default=timezone.now)
    sound = models.TextField(null=True)

    def send_to_device(self) -> None:
        APNSDevice.objects.filter(user=self.user).send_message(
            message=self.message,
            sound=self.sound,
            extra={
                "type": self.type,
                "data": self.data,
            }
        )

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    body = models.TextField()
    timestamp = models.FloatField(default=current_timestamp)

    def save(self, *args, **kwargs) -> None:
        Message.objects.filter(
            (Q(sender=self.sender)|Q(receiver=self.sender))&
            Q(timestamp__lte=current_timestamp()-timedelta(minutes=10).total_seconds())
        ).delete()
        super().save(*args, **kwargs)

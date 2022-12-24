""" Defines API for Users """
from django.db.models import Q
from django.core.mail import send_mail
from django.forms import ValidationError
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.serializers import EmailField, IntegerField, ListField, ModelSerializer, Serializer
from rest_framework.response import Response

from users.models import EmailAuthentication, Match, PhoneAuthentication, Question, User

import sys
sys.path.append(".")
from twilio_config import twilio_client, twilio_phone_number

# Email API
HOST_EMAIL = "lorem-ipsum@usc.edu"

class SendEmailCodeSerializer(ModelSerializer):
    """ SendEmailCode Parameters """

    class Meta:
        """ JSON fields from EmailAuthentication """
        model = EmailAuthentication
        fields = (
          'email',
          'proxy_uuid',
        )

    def validate_email(self, email):
        """ Emails should be from USC only """
        domain = email.split('@')[-1]
        if domain not in ['usc.edu']:
            raise ValidationError('non usc email')
        return email

class SendEmailCode(CreateAPIView):
    """ Send email with verification code """
    serializer_class = SendEmailCodeSerializer

    def create(self, request, *args, **kwargs):
        email_request = SendEmailCodeSerializer(data=request.data)
        email_request.is_valid(raise_exception=True)
        email = email_request.data.get('email').lower()
        proxy_uuid = email_request.data.get('proxy_uuid')

        user_matches = User.objects.filter(email=email)
        if user_matches.exists():
            return Response(
              {
                'email': 'email taken'
              },
              status.HTTP_400_BAD_REQUEST,
            )

        EmailAuthentication.objects.filter(email__iexact=email).delete()
        auth = EmailAuthentication.objects.create(email=email, proxy_uuid=proxy_uuid)
        self.send_email(email, auth.code)

        return Response(email_request.data, status.HTTP_201_CREATED)

    def send_email(self, email, code) -> None:
        """ Sends email with code to the provided email """
        send_mail(
            "here's your code",
            f"your email verification code for usc dating club is {code}",
            HOST_EMAIL,
            [email],
            fail_silently=False,
        )

# Verify Email Code
class VerifyEmailCodeSerializer(ModelSerializer):
    """ VerifyEmailCode Parameters """

    class Meta:
        """ JSON fields from EmailAuthentication """
        model = EmailAuthentication
        fields = (
          'email',
          'code',
          'proxy_uuid',
        )

class VerifyEmailCode(UpdateAPIView):
    """ Verify email with provided code """
    def update(self, request, *args, **kwargs):
        code_request = VerifyEmailCodeSerializer(data=request.data)
        code_request.is_valid(raise_exception=True)
        email = code_request.data.get('email')
        code = code_request.data.get('code')
        proxy_uuid = code_request.data.get('proxy_uuid')

        matches = EmailAuthentication.objects.filter(
          email__iexact=email, 
          code=code,
          proxy_uuid=proxy_uuid,
        )
        if not matches.exists():
            return Response(
              {
                'code': 'code does not match'
              },
              status.HTTP_400_BAD_REQUEST)

        matches.update(is_verified=True)
        return Response(code_request.data, status.HTTP_200_OK)

# Send Phone Code
class SendPhoneCodeSerializer(ModelSerializer):
    """ SendPhoneCode parameters """

    class Meta:
        """ JSON fields from PhoneAuthentication """
        model = PhoneAuthentication
        fields = (
          'phone_number',
          'proxy_uuid',
        )

class SendPhoneCode(CreateAPIView):
    """ Sends verification code to phone """
    serializer_class = SendPhoneCodeSerializer
    
    def create(self, request, *args, **kwargs):
        phone_request = SendPhoneCodeSerializer(data=request.data)
        phone_request.is_valid(raise_exception=True)
        phone_number = phone_request.data.get('phone_number')
        proxy_uuid = phone_request.data.get('proxy_uuid')

        user_matches = User.objects.filter(phone_number=phone_number)
        if user_matches.exists():
            return Response(
              {
                'phone_number': 'phone number taken'
              },
              status.HTTP_400_BAD_REQUEST,
            )

        PhoneAuthentication.objects.filter(phone_number=phone_number).delete()
        phone_auth = PhoneAuthentication.objects.create(
          phone_number=phone_number,
          proxy_uuid=proxy_uuid,
        )
        self.send_text(phone_number, phone_auth.code)

        return Response(phone_request.data, status.HTTP_201_CREATED)

    def send_text(self, phone_number, code):
        """ Sends verification text to phone number """
        twilio_client.messages.create(
            body=f"your code for usc dating club is {code}",
            from_=twilio_phone_number,
            to=str(phone_number),
        )
    
# Verify Phone Code [and/or Login]
class VerifyPhoneCodeSerializer(ModelSerializer):
    """ VerifyPhoneCode parameters """

    class Meta:
        """ JSON fields from PhoneAuthentication """
        model = PhoneAuthentication
        fields = (
          'phone_number',
          'code',
          'proxy_uuid',
        )

class VerifyPhoneCode(UpdateAPIView):
    """ Verifies phone number with code """

    def update(self, request, *args, **kwargs):
        code_request = VerifyPhoneCodeSerializer(data=request.data)
        code_request.is_valid(raise_exception=True)
        phone_number = code_request.data.get('phone_number')
        code = code_request.data.get('code')
        proxy_uuid = code_request.data.get('proxy_uuid')

        matches = PhoneAuthentication.objects.filter(
          phone_number=phone_number,
          code=code,
          proxy_uuid=proxy_uuid,
        )
        if not matches.exists():
            return Response(
              {
                'code': 'code does not match'
              },
              status.HTTP_400_BAD_REQUEST
            )
        
        matches.update(is_verified=True)
        return Response(code_request.data, status.HTTP_200_OK)

# Register User
class RegisterUserSerializer(ModelSerializer):
    """ RegisterUser parameters """

    class Meta:
        """ JSON fields from User """
        model = User
        fields = (
          'email',
          'phone_number',
          'first_name',
          'last_name',
          'sex_identity',
          'sex_preference',
        )

class RegisterUser(CreateAPIView):
    """ Registers user """
    serializer_class = RegisterUserSerializer

    def create(self, request, *args, **kwargs):
        register_request = RegisterUserSerializer(data=request.data)
        register_request.is_valid(raise_exception=True)
        phone_number = register_request.data.get('phone_number')
        email = register_request.data.get('email')

        phone_match = PhoneAuthentication.objects.filter(
          phone_number=phone_number,
          is_verified=True,
        )
        email_match = EmailAuthentication.objects.filter(
          email=email,
          is_verified=True,
        )

        if not phone_match.exists() or not email_match.exists():
            return Response(
              {
                'phone_number': 'no unregistered phone',
                'email': 'no unregistered email',
              },
              status.HTTP_400_BAD_REQUEST
            )

        if phone_match[0].proxy_uuid != email_match[0].proxy_uuid:
            return Response(
              {
                'phone_number': 'phone does not match email',
                'email': 'email does not match phone',
              },
              status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)

# Post Survey Answers
class PostSurveyAnswersSerializer(ModelSerializer):
    """ PostSurveyAnswers parameters """
    email = EmailField()
    responses = ListField(child=ListField(child=IntegerField))

class PostSurveyAnswers(CreateAPIView):
    """ Post survey answers """

    def create(self, request, *args, **kwargs):
        survey_request = PostSurveyAnswersSerializer(data=request.data)
        survey_request.is_valid(raise_exception=True)
        email = survey_request.data.get('email')
        q_responses = survey_request.data.get('responses')

        user_match = User.objects.filter(email=email)
        if not user_match:
            return Response(
              {
                'email': 'email does not exist'
              },
              status.HTTP_400_BAD_REQUEST,
            )
        
        for q_type, q_answer in q_responses:
            Question.objects.create(
              type=q_type,
              answre=q_answer,
              user=user_match,
            )
        
        return Response(survey_request.data, status.HTTP_201_CREATED)

# UpdateLocation
class UpdateLocationSerializer(ModelSerializer):
    """" UpdateLocation parameters """

    class Meta:
        """ JSON fields from User """
        model = User
        fields = (
          'latitude',
          'longitude',
        )

class NearbyUserSerializer(ModelSerializer):
    """ Limited information about nearby users """
    class Meta:
        """ JSON fields from User """
        model = User
        fields = (
          'id',
          'first_name',
          'last_name',
          'sex_identity',
          'sex_preference',
        )

class UpdateLocation(UpdateAPIView):
    """ List nearby users to a location """

    serializer_class = NearbyUserSerializer

    def update(self, request, *args, **kwargs):
        location_request = UpdateLocationSerializer(data=request.data)
        location_request.is_valid(raise_exception=True)

        latitude = location_request.data.get('latitude')
        longitude = location_request.data.get('longitude')

        within_latitude = (
          Q(latitude__isnull=False)&
          Q(latitude__lte=latitude+.001)&
          Q(latitude__gte=latitude-.001)
        )
        within_longitude = (
          Q(longitude__isnull=False)&
          Q(longitude__lte=longitude+.001)&
          Q(longitude__gte=longitude-.001)
        )

        nearby_users = User.objects.filter(
          within_latitude & within_longitude
        )
        nearby_users_list = [
          NearbyUserSerializer(nearby_user).data
          for nearby_user in nearby_users
        ]
        return Response(
          nearby_users_list,
          status.HTTP_200_OK,
        )

# Match Users
class MatchUsersSerializer(Serializer):
    """ MatchUsers parameters """
    email1 = EmailField()
    email2 = EmailField()

class MatchUsers(CreateAPIView):
    """ Matches two users """
    
    def create(self, request, *args, **kwargs):
        match_request = MatchUsersSerializer(data=request.data)
        match_request.is_valid()

        email1 = match_request.data.get('email1')
        email2 = match_request.data.get('email2')
        [email1, email2] = sorted([email1, email2])

        user1 = User.objects.filter(email=email1)
        user2 = User.objects.filter(email=email2)

        if not user1.exists() or not user2.exists():
            return Response(
              {
                'email1': 'email1 or email2 does not exist',
                'email2': 'email1 or email2 does not exist',
              },
              status.HTTP_400_BAD_REQUEST,
            )

        Match.objects.create(user1=user1, user2=user2)

        return Response(
          match_request.data,
          status.HTTP_201_CREATED,
        )

    def send_match_notification(user1, user2):
        pass

# Delete Account
class DeleteAccountSerializer(Serializer):
    """" DeleteAccount parameters """
    email = EmailField()

class DeleteAccount(DestroyAPIView):
    """ Deletes account """
    
    def destroy(self, request, *args, **kwargs):
        delete_request = DeleteAccountSerializer(data=request.data)
        delete_request.is_valid()
        email = delete_request.data.get('email')

        User.objects.filter(email=email).delete()

        return Response(delete_request.data, status.HTTP_204_NO_CONTENT)

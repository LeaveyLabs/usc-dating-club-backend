""" Defines API functions for Users """
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.serializers import ModelSerializer
from rest_framework.response import Response

from users.models import EmailAuthentication, PhoneAuthentication, User

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

class SendEmailCode(CreateAPIView):
    """ Send email with verification code """
    serializer_class = SendEmailCodeSerializer

    def create(self, request, *args, **kwargs):
        email_request = SendEmailCodeSerializer(data=request.data)
        email_request.is_valid(raise_exception=True)
        email = email_request.data.get('email').lower()
        proxy_uuid = email_request.data.get('proxy_uuid')

        EmailAuthentication.objects.filter(email__iexact=email).delete()
        auth = EmailAuthentication.objects.create(email=email, proxy_uuid=proxy_uuid)
        self.send_email(email, auth.code)

        return super().create(request, *args, **kwargs)

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

        PhoneAuthentication.objects.filter(phone_number=phone_number).delete()
        phone_auth = PhoneAuthentication.objects.create(
          phone_number=phone_number,
          proxy_uuid=proxy_uuid,
        )
        self.send_text(phone_number, phone_auth.code)

        return super().create(request, *args, **kwargs)

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
                'phone': 'no unregistered phone',
                'email': 'no unregistered email',
              },
              status.HTTP_400_BAD_REQUEST
            )
        
        if phone_match[0].proxy_uuid is not email_match[0].proxy_uuid:
            return Response(
              {
                'phone': 'phone does not match email',
                'email': 'email does not match phone',
              },
              status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)

# Post Survey Answers
# Query Nearby Users
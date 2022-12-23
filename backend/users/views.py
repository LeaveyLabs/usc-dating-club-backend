""" Defines API functions for Users """
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.serializers import ModelSerializer
from rest_framework.response import Response

from users.models import EmailAuthentication, PhoneAuthentication

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
                'code': "code does not match"
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
# Register User
# Post Survey Answers
# Query Nearby Users
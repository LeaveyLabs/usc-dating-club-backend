""" Defines API functions for Users """
import json

from django.core.mail import send_mail
from django.shortcuts import render
from enum import Enum
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.parsers import FormParser
from rest_framework.serializers import ModelSerializer
from rest_framework.response import Response
from users.models import EmailAuthentication

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
        matches = EmailAuthentication.objects.filter(email__iexact=email, code=code)
        if not matches.exists():
            return Response(
              {
                EmailKeys.CODE: "code does not match"
              },
              status.HTTP_400_BAD_REQUEST)

        matches.update(is_verified=True)
        return super().update(request, *args, **kwargs)

# Send Phone Phone
# Verify Phone Code [and/or Login]
# Register User
# Post Survey Answers
# Query Nearby Users
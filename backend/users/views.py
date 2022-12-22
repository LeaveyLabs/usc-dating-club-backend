""" Defines API functions for Users """
import json

from django.core.mail import send_mail
from django.shortcuts import render
from enum import Enum
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from users.models import EmailAuthentication

# Email API
HOST_EMAIL = "lorem-ipsum@usc.edu"

class EmailKeys:
    """ JSON keys for email requests """
    EMAIL = "email"
    CODE = "code"

class EmailRequestParser:
    """ Retrieves relevant keys from email request """

    @staticmethod
    def extract_email(request) -> str:
        """ Returns email from request body """
        try:
          email_json = json.loads(str(request.body, encoding='utf-8'))
          return email_json[EmailKeys.EMAIL].lower()
        except (KeyError, json.decoder.JSONDecodeError):
          return None
    
    @staticmethod
    def extract_code(request) -> str:
        """ Returns code from request body """
        try:
          email_json = json.loads(str(request.body, encoding='utf-8'))
          return email_json[EmailKeys.CODE]
        except (KeyError, json.decoder.JSONDecodeError):
          return None


class SendEmailCode(CreateAPIView):
    """ Send email with verification code """
    def create(self, request, *args, **kwargs):
        print(request.body)
        email = EmailRequestParser.extract_email(request)
        if not email:
            return Response(
              {
                EmailKeys.EMAIL: "email required"
              },
              status.HTTP_400_BAD_REQUEST)
        
        EmailAuthentication.objects.filter(email__iexact=email).delete()
        auth = EmailAuthentication.objects.create(email=email)
        self.send_email(email, auth.code)

        return Response({}, status.HTTP_201_CREATED)

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
class VerifyEmailCode(UpdateAPIView):
    """ Verify email with provided code """
    def update(self, request, *args, **kwargs):
        email = EmailRequestParser.extract_email(request)
        code = EmailRequestParser.extract_code(request)
        matches = EmailAuthentication.objects.filter(email__iexact=email, code=code)
        if not matches.exists():
            return Response(
              {
                EmailKeys.CODE: "code does not match"
              },
              status.HTTP_400_BAD_REQUEST)

        matches.update(is_verified=True)
        return Response({}, status.HTTP_200_OK)

# Send Phone Phone
# Verify Phone Code [and/or Login]
# Register User
# Post Survey Answers
# Query Nearby Users
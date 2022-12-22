""" Defines API functions for Users """
import json

from django.shortcuts import render
from enum import Enum
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

""" Email API """

class EmailKeys(Enum):
    EMAIL = "email"
    CODE = "code"

# Send Email Code
class SendEmailCode(CreateAPIView):
    def create(self, request, *args, **kwargs):
        email_json = json.loads(str(request.body, encoding='utf-8'))
        if not EmailKeys.EMAIL in email_json:
            return Response({"email": "email required"}, status.HTTP_400_BAD_REQUEST)
        email = email_json[EmailKeys.EMAIL]
        return super().create(request, *args, **kwargs)

# Verify Email Code

# Send Phone Phone
# Verify Phone Code [and/or Login]
# Register User
# Post Survey Answers
# Query Nearby Users
from django.core import mail
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory
from users.models import EmailAuthentication
from users.views import SendEmailCode, VerifyEmailCode
from uuid import uuid4

class SendEmailCodeTest(TestCase):
    """ Test email sender API """

    def test_basic_usc_email_sends_code(self):
        """ Verify kevinsun@usc.edu """
        request = APIRequestFactory().post(
          path="send-email-code/",
          data={
              "email": "kevinsun@usc.edu",
              "proxy_uuid": uuid4(),
          }
        )
        response = SendEmailCode.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(EmailAuthentication.objects.filter(email="kevinsun@usc.edu"))

class VerifyEmailCodeTest(TestCase):
    """ Test email verifier API """

    def setUp(self):
        self.basic_email = 'BasicEmail@usc.edu'
        self.basic_code = '123456'
        self.basic_uuid = uuid4()

        EmailAuthentication.objects.create(
          email=self.basic_email,
          code=self.basic_code,
          proxy_uuid=self.basic_uuid,
        )

    def test_matching_email_and_code_verifies_email(self):
        request = APIRequestFactory().put(
          path='verify-email-code/',
          data={
              "email": self.basic_email,
              "code": self.basic_code,
              "proxy_uuid": self.basic_uuid,
          }
        )
        response = VerifyEmailCode.as_view()(request)

        email_auth = EmailAuthentication.objects.get(
            email=self.basic_email,
            code=self.basic_code,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(email_auth.is_verified)


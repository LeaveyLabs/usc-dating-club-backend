from django.core import mail
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory
from uuid import uuid4

from users.models import EmailAuthentication, PhoneAuthentication, User
from users.views import RegisterUser, SendEmailCode, SendPhoneCode, VerifyEmailCode, VerifyPhoneCode

import sys
sys.path.append(".")
from twilio_config import TwilioTestClientMessages

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

class SendPhoneCodeTest(TestCase):
    """ Test text sender API """

    def test_basic_phone_number_sends_code(self):
        """ Verify +13108741292 """
        request = APIRequestFactory().post(
          path="send-phone-code/",
          data={
              "phone_number": "+13108741292",
              "proxy_uuid": uuid4(),
          }
        )
        response = SendPhoneCode.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(TwilioTestClientMessages.created), 1)
        self.assertTrue(PhoneAuthentication.objects.filter(phone_number="+13108741292"))

class VerifyPhoneCodeTest(TestCase):
    """ Test phone verifier API """

    def setUp(self):
        self.basic_phone_number = "+13108741292"
        self.basic_code = "123456"
        self.basic_uuid = uuid4()

        PhoneAuthentication.objects.create(
          phone_number=self.basic_phone_number,
          code=self.basic_code,
          proxy_uuid=self.basic_uuid,
        )

    def test_matching_phone_number_and_code_verifies_phone(self):
        """ Verify +13108741292 with 123456 """
        request = APIRequestFactory().put(
          path='verify-phone-code/',
          data={
            'phone_number': self.basic_phone_number,
            'code': self.basic_code,
            'proxy_uuid': self.basic_uuid,
          }
        )
        response = VerifyPhoneCode.as_view()(request)

        phone_auth = PhoneAuthentication.objects.get(
          phone_number=self.basic_phone_number,
          code=self.basic_code,
          proxy_uuid=self.basic_uuid,
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue(phone_auth.is_verified)

class RegisterUserTest(TestCase):
    """ Tests user registration API """
    def setUp(self):
        self.basic_email = "kevinsun@usc.edu"
        self.basic_phone_number = "+13108741292"
        self.basic_first_name = "Kevin"
        self.basic_last_name = "Sun"
        self.basic_sex_identity = 0
        self.basic_sex_preference = 1
        self.basic_proxy_uuid = uuid4()

        EmailAuthentication.objects.create(
          email=self.basic_email,
          proxy_uuid=self.basic_proxy_uuid,
          is_verified=True,
        )
        PhoneAuthentication.objects.create(
          phone_number=self.basic_phone_number,
          proxy_uuid=self.basic_proxy_uuid,
          is_verified=True,
        )

    def test_basic_user_info_registers_user(self):
        request = APIRequestFactory().post(
          path='register-user/',
          data={
            'email': self.basic_email,
            'phone_number': self.basic_phone_number,
            'first_name': self.basic_first_name,
            'last_name': self.basic_last_name,
            'sex_identity': self.basic_sex_identity,
            'sex_preference': self.basic_sex_preference,
          }
        )
        response = RegisterUser.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(
          email=self.basic_email,
          phone_number=self.basic_phone_number,
          first_name=self.basic_first_name,
          last_name=self.basic_last_name,
          sex_identity=self.basic_sex_identity,
          sex_preference=self.basic_sex_preference,
        ))

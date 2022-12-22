from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory
from users.views import EmailKeys, EmailRequestParser, SendEmailCode

class SendEmailCodeTest(TestCase):
    """ Test email sender API """

    def test_basic_usc_email_sends_code(self):
        """ Verify kevinsun@usc.edu """
        request = APIRequestFactory().post(
          path="send-email-code/",
          data={
            EmailKeys.EMAIL: "kevinsun@usc.edu",
          }
        )
        response = SendEmailCode().post(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

# Request Parser Tests

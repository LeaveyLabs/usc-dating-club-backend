""" Tests for User APIs """
import random
from django.core import mail
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIRequestFactory
from uuid import uuid4

from users.models import EmailAuthentication, Match, Notification, NumericalResponse, PhoneAuthentication, Question, TextResponse, User
from users.views import CompleteUserSerializer, DeleteAccount, GetQuestions, PostSurveyAnswers, QuestionSerializer, RegisterUser, SendEmailCode, SendPhoneCode, UpdateLocation, AcceptMatch, UpdateMatchableStatus, VerifyEmailCode, VerifyPhoneCode

import sys
sys.path.append(".")
from twilio_config import TwilioTestClientMessages

class APIRequestFactoryWithToken(APIRequestFactory):
    token = None

    def get(self, *args, **kwargs):
        return super().get(HTTP_AUTHORIZATION=f'Token {self.token}', *args, **kwargs)

    def put(self, *args, **kwargs):
        return super().put(HTTP_AUTHORIZATION=f'Token {self.token}', *args, **kwargs)
    
    def patch(self, *args, **kwargs):
        return super().patch(HTTP_AUTHORIZATION=f'Token {self.token}', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return super().delete(HTTP_AUTHORIZATION=f'Token {self.token}', *args, **kwargs)


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

    def test_already_taken_usc_email_does_not_send_code(self):
        """ Verify taken.usc.email@usc.edu"""
        User.objects.create(email='taken.usc.email@usc.edu')
        request = APIRequestFactory().post(
          path="send-email-code/",
          data={
            "email": "taken.usc.email@usc.edu",
            "proxy_uuid": uuid4(),
          }
        )
        response = SendEmailCode.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(EmailAuthentication.objects.filter(email="taken.usc.email@usc.edu"))
    
    def test_non_usc_email_does_not_send_code(self):
        """ Verify kevinsun127@gmail.com """
        request = APIRequestFactory().post(
          path="send-email-code/",
          data={
            "email": "kevinsun127@gmail.com",
            "proxy_uuid": uuid4(),
          }
        )
        response = SendEmailCode.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(EmailAuthentication.objects.filter(email="kevinsun127@gmail.com"))


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
        """ Verify kevinsun@usc.edu with 123456 """
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
    def setUp(self) -> None:
        TwilioTestClientMessages.created = []
        return super().setUp()

    def test_basic_phone_number_sends_code(self) -> None:
        """ Verify +13108741292 """
        request = APIRequestFactory().post(
          path="send-phone-code/",
          data={
              "phone_number": "+13108741292",
              "proxy_uuid": uuid4(),
              "is_registration": True,
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

    def test_verifying_existing_phone_number_returns_user(self):
        """ Verify +13108741292 with 123456 """
        user = User.objects.create(phone_number=self.basic_phone_number)
        user_json = CompleteUserSerializer(user).data

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
        self.assertTrue(response.data, user_json)


class RegisterUserTest(TestCase):
    """ Tests user registration API """
    def setUp(self):
        self.basic_email = "kevinsun@usc.edu"
        self.basic_phone_number = "+13108741292"
        self.basic_first_name = "Kevin"
        self.basic_last_name = "Sun"
        self.basic_sex_identity = User.SexChoices.MALE
        self.basic_sex_preference = User.SexChoices.FEMALE
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
        """ Register Kevin Sun (kevinsun@usc.edu) """
        registration_data = {
          'email': self.basic_email,
          'phone_number': self.basic_phone_number,
          'first_name': self.basic_first_name,
          'last_name': self.basic_last_name,
          'sex_identity': self.basic_sex_identity,
          'sex_preference': self.basic_sex_preference,
        }

        request = APIRequestFactory().post(
          path='register-user/',
          data=registration_data,
        )
        response = RegisterUser.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertTrue(User.objects.filter(
          email=self.basic_email,
          phone_number=self.basic_phone_number,
          first_name__iexact=self.basic_first_name,
          last_name__iexact=self.basic_last_name,
          sex_identity=self.basic_sex_identity,
          sex_preference=self.basic_sex_preference,
        ))


def random_user(id, sex_identity=None, sex_preference=None) -> User:
    """ Instantiates a random user """
    sex_identity = sex_identity if sex_identity else random.choice(User.SEX_CHOICES)[0]
    sex_preference = sex_preference if sex_preference else random.choice(User.SEX_CHOICES)[0]
    phone_body = "".join([str(random.randint(0,9)) for _ in range(7)])
    return User(
        id=id,
        email=f'{id}@usc.edu',
        phone_number=f'+1310{phone_body}',
        first_name="Kevin",
        last_name="Sun",
        sex_identity=sex_identity,
        sex_preference=sex_preference,
    )


class UpdateLocationTest(TestCase):
    """ Test location update """

    def setUp(self):
        self.user1 = random_user(1, User.SexChoices.MALE, User.SexChoices.FEMALE)
        self.user2 = random_user(2, User.SexChoices.FEMALE, User.SexChoices.MALE)

        self.user1.is_matchable = True
        self.user2.is_matchable = True

        self.user1.save()
        self.user2.save()
      
    def test_basic_location_update_near_compatible_user_matches_user(self):
        """" 
        Both people are:
        - in the same location
        - opposite sex preferences
        - similar compatibility.
        """
        self.user1.latitude = 0
        self.user1.longitude = 0
        self.user1.save()

        Question.objects.create(id=1, category='test1', is_numerical=True)
        NumericalResponse.objects.create(question_id=1, answer=1, user=self.user1)
        NumericalResponse.objects.create(question_id=1, answer=1, user=self.user2)

        Question.objects.create(id=2, category='test2', is_numerical=False)
        TextResponse.objects.create(question_id=2, answer='hello', user=self.user1)
        TextResponse.objects.create(question_id=2, answer='hello', user=self.user2)

        request = APIRequestFactory().put(
          path='update-location/',
          data={
            'email': self.user2.email,
            'latitude': 0,
            'longitude': 0,
          }
        )
        response = UpdateLocation.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
          Match.objects.filter(user1=self.user1, user2=self.user2) or
          Match.objects.filter(user1=self.user2, user2=self.user1)
        )
        self.assertTrue(Notification.objects.filter(user=self.user1))
        self.assertTrue(Notification.objects.filter(user=self.user2))

    def test_basic_location_update_near_sexually_incompatible_user_does_not_match_user(self):
        """ Both people are in the same location, but nonmatching sexual preference """
        self.user1.latitude = 0
        self.user1.longitude = 0
        self.user1.sex_identity = 'm'
        self.user1.sex_preference = 'f'

        self.user2.sex_identity = 'm'
        self.user2.sex_preference = 'f'

        self.user1.save()
        self.user2.save()

        request = APIRequestFactory().put(
          path='update-location/',
          data={
            'email': self.user2.email,
            'latitude': 0,
            'longitude': 0,
          }
        )
        response = UpdateLocation.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
          Match.objects.filter(user1=self.user1, user2=self.user2) or
          Match.objects.filter(user1=self.user2, user2=self.user1)
        )
        self.assertFalse(Notification.objects.filter(user=self.user1))
        self.assertFalse(Notification.objects.filter(user=self.user2))

    def test_basic_location_update_near_test_incompatible_user_matches_user(self):
        """" 
        Very different test results.
        """
        self.user1.latitude = 0
        self.user1.longitude = 0
        self.user1.save()

        Question.objects.create(id=1, category='test1', is_numerical=True)
        NumericalResponse.objects.create(question_id=1, answer=1, user=self.user1)
        NumericalResponse.objects.create(question_id=1, answer=7, user=self.user2)

        Question.objects.create(id=2, category='test2', is_numerical=False)
        TextResponse.objects.create(question_id=2, answer='hello', user=self.user1)
        TextResponse.objects.create(question_id=2, answer='goodbye', user=self.user2)

        request = APIRequestFactory().put(
          path='update-location/',
          data={
            'email': self.user2.email,
            'latitude': 0,
            'longitude': 0,
          }
        )
        response = UpdateLocation.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
          Match.objects.filter(user1=self.user1, user2=self.user2) or
          Match.objects.filter(user1=self.user2, user2=self.user1)
        )
        self.assertFalse(Notification.objects.filter(user=self.user1))
        self.assertFalse(Notification.objects.filter(user=self.user2))


    def test_old_location_update_does_not_match_user(self) -> None:
        """ Try to match with a user who updated their location yesterday """
        self.user1.latitude = 0
        self.user1.longitude = 0
        self.user1.loc_update_time = timezone.now() - timezone.timedelta(days=1)
        self.user1.save()

        request = APIRequestFactory().put(
          path='update-location/',
          data={
            'email': self.user2.email,
            'latitude': 0,
            'longitude': 0,
          }
        )
        response = UpdateLocation.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
          Match.objects.filter(user1=self.user1, user2=self.user2) or
          Match.objects.filter(user1=self.user2, user2=self.user1)
        )
        self.assertFalse(Notification.objects.filter(user=self.user1))
        self.assertFalse(Notification.objects.filter(user=self.user2))

class PostSurveyAnswersTest(TestCase):
    def setUp(self):
        self.user1 = random_user(1, User.SexChoices.MALE, User.SexChoices.FEMALE)

        self.user1.save()

        Question.objects.create(id=0, category=0, is_numerical=True)
        Question.objects.create(id=1, category=1, is_numerical=True)
        Question.objects.create(id=2, category=2, is_numerical=True)
    
    def test_basic_numerical_survey_answers_should_create_numerical_responses(self):
        """ Post (0-2, 1-3) tuples with an existing user """
        Question.objects.filter(id=0).update(is_numerical=True)
        Question.objects.filter(id=1).update(is_numerical=True)
        Question.objects.filter(id=2).update(is_numerical=True)

        request = APIRequestFactory().post(
          path='post-survey-answers/',
          data={
            'email': self.user1.email,
            'responses': [
              {
                'question_id': 0,
                'answer': 1,
              },
              {
                'question_id': 1,
                'answer': 2,
              },
              {
                'question_id': 2,
                'answer': 3,
              }
            ]
          },
          format='json',
        )
        response = PostSurveyAnswers.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(NumericalResponse.objects.filter(user=self.user1)), 3)

    def test_basic_text_survey_answers_should_create_text_responses(self):
        """ Post (0-2, 1-3) tuples with an existing user """
        Question.objects.filter(id=0).update(is_numerical=False)
        Question.objects.filter(id=1).update(is_numerical=False)
        Question.objects.filter(id=2).update(is_numerical=False)

        request = APIRequestFactory().post(
          path='post-survey-answers/',
          data={
            'email': self.user1.email,
            'responses': [
              {
                'question_id': 0,
                'answer': 'this',
              },
              {
                'question_id': 1,
                'answer': 'is',
              },
              {
                'question_id': 2,
                'answer': 'test',
              }
            ]
          },
          format='json',
        )
        response = PostSurveyAnswers.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(TextResponse.objects.filter(user=self.user1)), 3)

    def test_basic_numerical_and_text_survey_answers_should_create_numerical_and_text_responses(self):
        """ Post (0-2, 1-3) tuples with an existing user """
        Question.objects.filter(id=0).update(is_numerical=False)
        Question.objects.filter(id=1).update(is_numerical=True)
        Question.objects.filter(id=2).update(is_numerical=True)

        request = APIRequestFactory().post(
          path='post-survey-answers/',
          data={
            'email': self.user1.email,
            'responses': [
              {
                'question_id': 0,
                'answer': 'this',
              },
              {
                'question_id': 1,
                'answer': 0,
              },
              {
                'question_id': 2,
                'answer': 5,
              }
            ]
          },
          format='json',
        )
        response = PostSurveyAnswers.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(NumericalResponse.objects.filter(user=self.user1)), 2)
        self.assertEqual(len(TextResponse.objects.filter(user=self.user1)), 1)


class DeleteAccountTest(TestCase):
    def setUp(self):
        self.user1 = random_user(1, User.SexChoices.MALE, User.SexChoices.FEMALE)

        self.user1.save()
    
    def test_delete_basic_account_should_delete_account(self):
        """ Delete kevinsun@usc.edu """
        request = APIRequestFactory().delete(
          path='delete-account/',
          data={
            'email': self.user1.email,
          }
        )
        response = DeleteAccount.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user1.id))

class UpdateMatchableStatusTest(TestCase):
    def setUp(self):
        self.user1 = random_user(1, User.SexChoices.MALE, User.SexChoices.FEMALE)

        self.user1.save()
    
    def test_basic_activate_matchable_status(self):
        """ Update is_matchable to True """
        request = APIRequestFactory().patch(
          path='update-matchable-status',
          data={
            'email': self.user1.email,
            'is_matchable': True,
          }
        )
        response = UpdateMatchableStatus.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.get(id=self.user1.id).is_matchable)

class UpdateMatchAcceptanceTest(TestCase):
    def setUp(self):
        self.user1 = random_user(1, User.SexChoices.MALE, User.SexChoices.FEMALE)
        self.user2 = random_user(2, User.SexChoices.FEMALE, User.SexChoices.MALE)

        self.user1.save()
        self.user2.save()

        Match.objects.create(user1=self.user1, user2=self.user2)
    
    def test_basic_match_acceptance(self):
        """ Update user1_accepted to True """
        request = APIRequestFactory().patch(
          path='update-match-acceptance',
          data={
            'user_id': self.user1.id,
            'partner_id': self.user2.id,
          }
        )
        response = AcceptMatch.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Match.objects.get(user1_id=self.user1.id).user1_accepted)
  

class GetQuestionsTest(TestCase):
    def setUp(self):
        self.question0 = Question.objects.create(id=0, category=0, is_numerical=True)
        self.question1 = Question.objects.create(id=1, category=1, is_numerical=True)
        self.question2 = Question.objects.create(id=2, category=2, is_numerical=True)

    def test_basic_get_questions_returns_all_questions(self):
        questions_json = [
            QuestionSerializer(self.question0).data,
            QuestionSerializer(self.question1).data,
            QuestionSerializer(self.question2).data,
        ]
        request = APIRequestFactory().get(
          path='get-questions/',
        )
        response = GetQuestions.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data[0], questions_json[0])
        self.assertCountEqual(response.data[1], questions_json[1])
        self.assertCountEqual(response.data[2], questions_json[2])
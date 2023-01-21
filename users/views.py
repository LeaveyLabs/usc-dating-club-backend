""" Defines API for Users """
import os

from django.db.models import Q, Count
from django.core.mail import send_mail
from django.forms import ValidationError
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.serializers import BooleanField, EmailField, IntegerField, ListField, CharField, ModelSerializer, Serializer, SerializerMethodField
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from users.models import EmailAuthentication, Match, NumericalQuestion, NumericalResponse, PhoneAuthentication, BaseQuestion, TextQuestion, TextResponse, User, WaitingEmail

import sys
sys.path.append(".")
from twilio_config import twilio_client, twilio_phone_number

# Email API
HOST_EMAIL = os.environ.get("EMAIL_HOST_USER")

class SendEmailCodeSerializer(ModelSerializer):
    """ SendEmailCode Parameters """

    class Meta:
        """ JSON fields from EmailAuthentication """
        model = EmailAuthentication
        fields = (
          'email',
          'proxy_uuid',
        )

    # def validate_email(self, email):
    #     """ Emails should be from USC only """
    #     domain = email.split('@')[-1]
    #     if domain not in ['usc.edu']:
    #         raise ValidationError('non usc email')
    #     return email

class SendEmailCode(CreateAPIView):
    """ Send email with verification code """
    serializer_class = SendEmailCodeSerializer
    permission_class = [AllowAny, ]

    def create(self, request, *args, **kwargs):
        email_request = SendEmailCodeSerializer(data=request.data)
        email_request.is_valid(raise_exception=True)
        email = email_request.data.get('email').lower()
        proxy_uuid = email_request.data.get('proxy_uuid')

        if not self.is_usc_email(email):
          WaitingEmail.objects.create(email=email)
          return Response(
            {
              'email': ['email added to waiting list']
            },
            status.HTTP_400_BAD_REQUEST,
          )

        user_matches = User.objects.filter(email=email)
        if user_matches.exists():
            return Response(
              {
                'email': ['email taken']
              },
              status.HTTP_400_BAD_REQUEST,
            )

        EmailAuthentication.objects.filter(email__iexact=email).delete()
        auth = EmailAuthentication.objects.create(email=email, proxy_uuid=proxy_uuid)

        if auth.email == os.environ.get('BACKDOOR_EMAIL'):
            auth.code = "123456"
            auth.save()
        else:
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

    def is_usc_email(self, email) -> bool:
        """ Emails should be from USC only """
        domain = email.split('@')[-1]
        return domain in ['usc.edu']

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
    serializer_class = VerifyEmailCodeSerializer
    permission_class = [AllowAny, ]

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
                'code': ['code does not match']
              },
              status.HTTP_400_BAD_REQUEST)

        matches.update(is_verified=True)
        return Response(code_request.data, status.HTTP_200_OK)

# Send Phone Code
class SendPhoneCodeSerializer(ModelSerializer):
    """ SendPhoneCode parameters """
    is_registration = BooleanField(default=False)

    class Meta:
        """ JSON fields from PhoneAuthentication """
        model = PhoneAuthentication
        fields = (
          'phone_number',
          'proxy_uuid',
          'is_registration',
        )

class SendPhoneCode(CreateAPIView):
    """ Sends verification code to phone """
    serializer_class = SendPhoneCodeSerializer
    permission_class = [AllowAny, ]
    
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

        if phone_auth.phone_number == os.environ.get('BACKDOOR_PHONE_NUMBER'):
            phone_auth.code = "123456"
            phone_auth.save()
        else:
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
class CompleteUserSerializer(ModelSerializer):
    """ Complete information about user """
    survey_responses = SerializerMethodField()
    token = SerializerMethodField()

    class Meta:
        """ JSON fields from User """
        model = User
        fields = (
          'id',
          'email',
          'phone_number',
          'first_name',
          'last_name',
          'sex_identity',
          'sex_preference',
          'survey_responses',
          'is_matchable',
          'token',
          'is_superuser',
        )

    def get_survey_responses(self, obj):
        try: obj.numerical_responses
        except: obj.numerical_responses = NumericalResponse.objects.filter(user_id=obj.id)

        try: obj.text_responses
        except: obj.text_responses = TextResponse.objects.filter(user_id=obj.id)

        numerical_responses = [
          SurveyResponseSerializer(question).data
          for question in obj.numerical_responses.all()
        ]
        text_responses = [
          SurveyResponseSerializer(question).data
          for question in obj.text_responses.all()
        ]

        return numerical_responses + text_responses

    def get_token(self, obj):
        try: obj.token
        except: obj.token = Token.objects.get(user_id=obj.id)
        return obj.token.key

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
    serializer_class = VerifyPhoneCodeSerializer
    permission_class = [AllowAny, ]

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
                'code': ['code does not match']
              },
              status.HTTP_400_BAD_REQUEST
            )

        matches.update(is_verified=True)

        users = User.objects.filter(phone_number=phone_number)
        if users.exists():
            user = users[0]
            return Response(
              CompleteUserSerializer(user).data,
              status.HTTP_200_OK,
            )

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
    permission_class = [AllowAny, ]

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
                'phone_number': ['unregistered phone'],
                'email': ['unregistered email'],
              },
              status.HTTP_400_BAD_REQUEST
            )

        if phone_match[0].proxy_uuid != email_match[0].proxy_uuid:
            return Response(
              {
                'phone_number': ['phone does not match email'],
                'email': ['email does not match phone'],
              },
              status.HTTP_400_BAD_REQUEST
            )

        registered_user = User.objects.create(**register_request.data)
        return Response(
          CompleteUserSerializer(registered_user).data,
          status.HTTP_201_CREATED,
        )

# Update User
class ReadOnlyUserSerializer(ModelSerializer):
    """ Read-only information about user """
    survey_responses = SerializerMethodField()

    class Meta:
        """ JSON fields from User """
        model = User
        fields = (
          'id',
          'email',
          'phone_number',
          'first_name',
          'last_name',
          'sex_identity',
          'sex_preference',
          'survey_responses',
          'is_matchable',
        )

# Post Survey Answers
class SurveyResponseSerializer(Serializer):
    question_id = IntegerField()
    answer = CharField()

class PostSurveyAnswersSerializer(Serializer):
    """ PostSurveyAnswers parameters """
    email = EmailField()
    responses = ListField(child=SurveyResponseSerializer())

class PostSurveyAnswers(CreateAPIView):
    """ Post survey answers """
    serializer_class = PostSurveyAnswersSerializer
    permission_class = [AllowAny, ]

    def create(self, request, *args, **kwargs):
        survey_request = PostSurveyAnswersSerializer(data=request.data)
        survey_request.is_valid(raise_exception=True)
        email = survey_request.data.get('email')
        q_responses = survey_request.data.get('responses')

        user_matches = User.objects.filter(email=email)
        if not user_matches:
            return Response(
              {
                'email': ['email does not exist']
              },
              status.HTTP_400_BAD_REQUEST,
            )
        user_match = user_matches[0]
        
        for q_response in q_responses:
            question_id = q_response.get('question_id')
            answer = q_response.get('answer')

            questions = BaseQuestion.objects.filter(id=question_id).prefetch_related(
              'numerical_question', 
              'text_question',
            )

            if not questions.exists():
                continue

            question = questions[0]

            numerical_questions = NumericalQuestion.objects.filter(base_question_id=question.id)
            text_questions = TextQuestion.objects.filter(base_question_id=question.id)

            if numerical_questions.exists():
                numerical_question = numerical_questions[0]
                try:
                    NumericalResponse.objects.create(
                      question_id=numerical_question.id,
                      answer=float(answer),
                      user=user_match,
                    )
                except:
                    continue
            
            if text_questions.exists():
                text_question = text_questions[0]
                TextResponse.objects.create(
                  question_id=text_question.id,
                  answer=answer,
                  user=user_match,
                )
        
        return Response(survey_request.data, status.HTTP_201_CREATED)

# UpdateLocation
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

class UpdateLocationSerializer(ModelSerializer):
    """" UpdateLocation parameters """
    email = EmailField()

    class Meta:
        """ JSON fields from User """
        model = User
        fields = (
          'email',
          'latitude',
          'longitude',
        )

class UpdateLocation(UpdateAPIView):
    """ List nearby users to a location """
    throttle_class = 'location'
    serializer_class = UpdateLocationSerializer
    permission_class = [AllowAny, ]

    def update(self, request, *args, **kwargs):
        location_request = UpdateLocationSerializer(data=request.data)
        location_request.is_valid(raise_exception=True)

        email = location_request.data.get('email')
        latitude = location_request.data.get('latitude')
        longitude = location_request.data.get('longitude')

        updated_users = User.objects.filter(email=email)\
          .prefetch_related('numerical_responses', 'text_responses')
        updated_users.update(
          latitude=latitude,
          longitude=longitude,
          loc_update_time=timezone.now()
        )

        if not updated_users.exists():
            return Response(
              {
                'email': ['email not found'],
              },
              status.HTTP_400_BAD_REQUEST,
            )

        updated_user = updated_users[0]

        if updated_user.is_matchable:
            self.match_with_nearby_users(updated_user, latitude, longitude)

        return Response(
          location_request.data,
          status.HTTP_200_OK,
        )
      
    def filter_compatible_users(self, user, nearby_users, 
        minimum_shared_numerical=1, minimum_shared_text=1):

        try: user.numerical_responses
        except: user.numerical_responses = NumericalResponse.objects.filter(user=user)

        try: user.text_responses
        except: user.text_responses = TextResponse.objects.filter(user=user)

        compatible_numerical_responses = Q()
        compatible_text_responses = Q()

        # either both above average or below average        
        for response in user.numerical_responses.all():
            compatible_numerical_responses |= (
              (
                Q(numerical_responses__question_id=response.question_id)&
                Q(numerical_responses__question__average__lte=response.answer)&
                Q(numerical_responses__answer__lte=response.answer)
              ) | (
                Q(numerical_responses__question_id=response.question_id)&
                Q(numerical_responses__question__average__gte=response.answer)&
                Q(numerical_responses__answer__gte=response.answer)
              )
            )
        for response in user.text_responses.all():
            compatible_text_responses |= (
              Q(text_responses__question_id=response.question_id)&
              Q(text_responses__answer=response.answer)
            )
        
        compatible_numerical_count = Count(
          'numerical_responses', 
          filter=compatible_numerical_responses
        )
        compatible_text_count = Count(
          'text_responses', 
          filter=compatible_text_responses
        )

        return nearby_users.annotate(
          compatible_numerical_count=compatible_numerical_count,
          compatible_text_count=compatible_text_count,
        ).filter(
          compatible_numerical_count__gte=minimum_shared_numerical,
          compatible_text_count__gte=minimum_shared_text,
        )

    def match_with_nearby_users(self, user, latitude, longitude) -> None:
        """ 
        Check if the match window has not expired. 
        If not, match with a nearby user. 
        """
        past_matches = Q(user1=user) | Q(user2=user)
        matches = Match.objects.filter(past_matches).order_by('-time')
        if matches and matches[0].has_expired(): return

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
        not_current_user = (
          ~Q(pk=user.pk)
        )
        sexually_preferred = (
          Q(sex_identity=user.sex_preference)&
          Q(sex_preference=user.sex_identity)
        )
        not_matched_before = (
          ~Q(match1__user1=user)&
          ~Q(match1__user2=user)&
          ~Q(match2__user1=user)&
          ~Q(match2__user2=user)
        )
        recent_update = (
          Q(loc_update_time__lte=timezone.now())&
          Q(loc_update_time__gte=timezone.now()-timezone.timedelta(minutes=15))
        )
        is_matchable = (
          Q(is_matchable=True)
        )

        nearby_users = User.objects.filter(
          within_latitude&
          within_longitude&
          not_current_user&
          sexually_preferred&
          not_matched_before&
          recent_update&
          is_matchable
        )

        if not nearby_users.exists(): return

        compatible_users = self.filter_compatible_users(
          user=user, 
          nearby_users=nearby_users
        )

        if not compatible_users.exists(): return
        
        compatible_user = compatible_users[0]

        Match.objects.create(
          user1=user,
          user2=compatible_user,
        )


# Delete Account
class DeleteAccountSerializer(Serializer):
    """" DeleteAccount parameters """
    email = EmailField()

class DeleteAccount(DestroyAPIView):
    """ Deletes account """
    serializer_class = DeleteAccountSerializer
    permission_class = [AllowAny, ]
    
    def destroy(self, request, *args, **kwargs):
        delete_request = DeleteAccountSerializer(data=request.data)
        delete_request.is_valid()
        email = delete_request.data.get('email')

        User.objects.filter(email=email).delete()

        return Response(delete_request.data, status.HTTP_204_NO_CONTENT)

# Deactivate Matches
class UpdateMatchableStatusSerializer(Serializer):
    email = EmailField()
    is_matchable = BooleanField()

class UpdateMatchableStatus(UpdateAPIView):
    """ Update whether the user is matchable """
    serializer_class = UpdateMatchableStatusSerializer
    permission_class = [AllowAny, ]

    def update(self, request, *args, **kwargs):
        matchable_request = UpdateMatchableStatusSerializer(data=request.data)
        matchable_request.is_valid(raise_exception=True)
        email = matchable_request.data.get('email')
        is_matchable = matchable_request.data.get('is_matchable')

        updated_users = User.objects.filter(email=email)
        updated_users.update(
          is_matchable=is_matchable,
        )

        if not updated_users:
            return Response(
              {
                'email': ['email not found'],
              },
              status.HTTP_400_BAD_REQUEST,
            )

        return Response(
          matchable_request.data,
          status.HTTP_200_OK,
        )

# Accept Match
class AcceptMatchSerializer(Serializer):
    user_id = IntegerField()
    partner_id = IntegerField()

class AcceptMatch(UpdateAPIView):
    """ Updates Match to reflect match acceptance """
    serializer_class = AcceptMatchSerializer
    permission_class = [AllowAny, ]

    def update(self, request, *args, **kwargs):
        update_request = AcceptMatchSerializer(data=request.data)
        update_request.is_valid(raise_exception=True)

        user_id = update_request.data.get('user_id')
        partner_id = update_request.data.get('partner_id')

        user1_id, user2_id = sorted([user_id, partner_id])
        matches = Match.objects.filter(
          user1_id=user1_id,
          user2_id=user2_id,
        )
        
        if user_id == user1_id:
            matches.update(user1_accepted=True)
        else:
            matches.update(user2_accepted=True)

        return Response(
          update_request.data,
          status.HTTP_200_OK,
        )

# Get Question List
class QuestionSerializer(ModelSerializer):
    class Meta:
        model = BaseQuestion
        fields = '__all__'

class GetQuestions(ListAPIView):
    serializer_class = QuestionSerializer
    permission_class = [AllowAny, ]
    queryset = BaseQuestion.objects.all()


class GetPageOrder(ListAPIView):
    queryset = BaseQuestion.objects.all()
    def list(self, request, *args, **kwargs):
        return Response(
          ["personality", "preferences", "values", "lifestyle",],
          status.HTTP_200_OK,
        )
  
# Force Create Match
class ForceCreateMatchSerializer(Serializer):
    user1_id = IntegerField()
    user2_id = IntegerField()

class ForceCreateMatch(CreateAPIView):
    serializer_class = ForceCreateMatchSerializer
    def create(self, request, *args, **kwargs):
        match_request = ForceCreateMatchSerializer(data=request.data)
        match_request.is_valid(raise_exception=True)
        user1_id = match_request.data.get('user1_id')
        user2_id = match_request.data.get('user2_id')

        Match.objects.filter(user1_id=user1_id, user2_id=user2_id).delete()
        Match.objects.filter(user1_id=user2_id, user2_id=user1_id).delete()
        Match.objects.create(user1_id=user1_id, user2_id=user2_id)

        return Response(
          match_request.data,
          status.HTTP_201_CREATED,
        )

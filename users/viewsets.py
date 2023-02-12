""" Defines REST viewsets for all models """
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from users.models import Category, NumericalQuestion, TextAnswerChoice, TextQuestion, User, Match, BaseQuestion, NumericalResponse, TextResponse, WaitingEmail, BannedEmail, Message


""" Serializers """


class ReadOnlyUserSerializer(ModelSerializer):
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
          'is_matchable',
        )

class MatchSerializer(ModelSerializer):
    class Meta:
        """ JSON fields from Match """
        model = Match
        fields = '__all__'

class WaitingEmailSerializer(ModelSerializer):
    class Meta:
        """ JSON fields from WaitingEmail """
        model = WaitingEmail
        fields = '__all__'

class BannedEmailSerializer(ModelSerializer):
    class Meta:
        """ JSON fields from BannedEmail """
        model = BannedEmail
        fields = '__all__'

class QuestionSerializer(ModelSerializer):
    is_numerical = SerializerMethodField()
    is_multiple_answer = SerializerMethodField()
    text_answer_choices = SerializerMethodField()

    class Meta:
        """ JSON fields from Question """
        model = BaseQuestion
        fields = '__all__'

    def get_is_numerical(self, obj):
        return NumericalQuestion.objects.\
            filter(base_question_id=obj.id).exists()
    
    def get_is_multiple_answer(self, obj):
        text_questions = TextQuestion.objects.\
            filter(base_question_id=obj.id)
        if not text_questions.exists():
            return False
        return text_questions[0].is_multiple_answer

    def get_text_answer_choices(self, obj):
        text_questions = TextQuestion.objects.\
            filter(base_question_id=obj.id).\
            prefetch_related('text_answer_choices')
        if not text_questions.exists():
            return []
        text_question = text_questions[0]
        return [
            text_answer_choice.answer 
            for text_answer_choice in 
            text_question.text_answer_choices.all()
        ]

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class NumericalQuestionSerializer(ModelSerializer):
    class Meta:
        """ JSON fields from Question """
        model = NumericalQuestion
        fields = '__all__'

class TextQuestionSerializer(ModelSerializer):
    class Meta:
        """ JSON fields from Question """
        model = TextQuestion
        fields = '__all__'

class TextAnswerChoiceSerializer(ModelSerializer):
    class Meta:
        """ JSON fields from Question """
        model = TextAnswerChoice
        fields = '__all__'

class NumericalResponseSerializer(ModelSerializer):
    class Meta:
        """ JSON fields from NumericalResponse """
        model = NumericalResponse
        fields = '__all__'

class TextResponseSerializer(ModelSerializer):
    class Meta:
        """ JSON fields from TextResponse """
        model = TextResponse
        fields = '__all__'

class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


""" Viewsets """


class UserViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    serializer_class = ReadOnlyUserSerializer
    permission_class = [AllowAny, ]
    queryset = User.objects.all()

class WaitingEmailViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing waiting emails.
    """
    serializer_class = WaitingEmailSerializer
    permission_class = [AllowAny, ]
    queryset = WaitingEmail.objects.all()

class BannedEmailViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing banned emails.
    """
    serializer_class = BannedEmailSerializer
    permission_class = [AllowAny, ]
    queryset = BannedEmail.objects.all()

class MatchViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing match instances.
    """
    serializer_class = MatchSerializer
    permission_class = [AllowAny, ]
    queryset = Match.objects.all()

class CategoryViewset(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_class = [AllowAny, ]
    queryset = Category.objects.all()

class QuestionViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing question instances.
    """
    serializer_class = QuestionSerializer
    permission_class = [AllowAny, ]
    queryset = BaseQuestion.objects.all()

    def list(self, *args, **kwargs):
        response = super().list(*args, **kwargs)
        numerical_questions = []
        text_questions = []
        for question in response.data:
            if question.get('is_numerical'):
                numerical_questions.append(question)
            else:
                text_questions.append(question)
        response.data = numerical_questions + text_questions
        return response

class TextQuestionViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing question instances.
    """
    serializer_class = TextQuestionSerializer
    permission_class = [AllowAny, ]
    queryset = TextQuestion.objects.all()

class NumericalQuestionViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing question instances.
    """
    serializer_class = NumericalQuestionSerializer
    permission_class = [AllowAny, ]
    queryset = NumericalQuestion.objects.all()

class TextAnswerChoiceViewset(viewsets.ModelViewSet):
    serializer_class = TextAnswerChoiceSerializer
    permission_class = [AllowAny, ]
    queryset = TextAnswerChoice.objects.all()


class NumericalResponseViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing numerical response instances.
    """
    serializer_class = NumericalResponseSerializer
    permission_class = [AllowAny, ]
    queryset = NumericalResponse.objects.all()

class TextResponseViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing text response instances.
    """
    serializer_class = TextResponseSerializer
    permission_class = [AllowAny, ]
    queryset = TextResponse.objects.all()

class MessageViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing message instances.
    """
    serializer_class = MessageSerializer
    permission_class = [AllowAny, ]
    queryset = Message.objects.all()

    def get_queryset(self, *args, **kwargs):
        user1_id = self.request.query_params.get('user1_id')
        user2_id = self.request.query_params.get('user2_id')

        return Message.objects.filter(
            (
                Q(sender=user1_id)&
                Q(receiver=user2_id)
            ) | (
                Q(receiver=user1_id)&
                Q(sender=user2_id)
            )  
        )
        
""" Defines REST viewsets for all models """
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.serializers import SerializerMethodField, ModelSerializer
from users.models import User, Match, Question, NumericalResponse, TextResponse


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

class QuestionSerializer(ModelSerializer):
    class Meta:
        """ JSON fields from Question """
        model = Question
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


""" Viewsets """


class UserViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    serializer_class = ReadOnlyUserSerializer
    permission_class = [AllowAny, ]
    queryset = User.objects.all()

class MatchViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing match instances.
    """
    serializer_class = MatchSerializer
    permission_class = [AllowAny, ]
    queryset = Match.objects.all()

class QuestionViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing question instances.
    """
    serializer_class = QuestionSerializer
    permission_class = [AllowAny, ]
    queryset = Question.objects.all()

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
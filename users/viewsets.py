""" Defines REST viewsets for all models """
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer
from users.models import User, Match, Question, NumericalResponse, TextResponse, WaitingEmail, BannedEmail


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

    def create(self, request, *args, **kwargs):
        match_request = MatchSerializer(data=request.data)
        match_request.is_valid()

        Match.objects.filter(
            user1=match_request.data.get('user1'),
            user2=match_request.data.get('user2'),
        ).delete()

        return super().create(request, *args, **kwargs)

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
""" Defines serialized representations for Users """

from rest_framework import serializers
from users.models import EmailAuthentication, PhoneAuthentication, User

class UserSerializer(serializers.ModelSerializer):
    """ JSON representation of User """

    class Meta:
        """ Pulling JSON fields from User """
        model = User
        fields = (
          'id',
          'email',
          'first_name',
          'last_name',
          'phone_number',
          'sex_identity',
          'sex_preference',
        )

class PhoneAuthenticationSerializer(serializers.ModelSerializer):
    """ JSON representation of PhoneAuthentication """

    class Meta:
        """ Pulling JSON fields from PhoneAuthentication """
        model = PhoneAuthentication
        fields = (
          'id',
          'phone_number',
          'is_verified',
          'proxy_uuid',
        )
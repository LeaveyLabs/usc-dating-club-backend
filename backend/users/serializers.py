from rest_framework import serializers
from users.models import User

class UserSerializer(serializers.ModelSerializer):
  """ JSON representation of User """
  
  class Meta:
    model = User
    fields = (
      'id', 
      'date_of_birth',
      'email', 
      'first_name', 
      'last_name', 
      'phone_number', 
      '')
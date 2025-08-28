from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "is_admin")


class SimpleUserSerializer(serializers.ModelSerializer):
    """
    A simple serializer for User model to avoid exposing sensitive data.
    Used for nested representations.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

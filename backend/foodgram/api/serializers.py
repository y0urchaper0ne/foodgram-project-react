from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipe.models import Ingridients, Tag, Recipe
from users.models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        value_lower = value.lower()
        username = User.objects.filter(username__iexact=value_lower)
        if username.exists():
            raise ValidationError('Пользователь с таким'
                                  ' username уже существует')
        return value_lower

    def validate_email(self, value):
        value_lower = value.lower()
        email = User.objects.filter(email__iexact=value_lower)
        if email.exists():
            raise ValidationError('Пользователь с таким'
                                  ' email уже существует')
        return value_lower
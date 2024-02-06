from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'password', 'account_created', 'account_updated')
        read_only_fields = ('id', 'account_created', 'account_updated')

    password = serializers.CharField(write_only=True)


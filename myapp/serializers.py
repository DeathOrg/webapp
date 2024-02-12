from rest_framework import serializers
from .models import User


class BaseUserSerializer(serializers.ModelSerializer):
    account_created = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)
    account_updated = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'account_created', 'account_updated']


class UserSerializer(BaseUserSerializer):
    pass


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'password']

    def __init__(self, instance, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        # Exclude other fields from update
        for field_name in self.fields.keys():
            if field_name not in ['first_name', 'last_name', 'password']:
                self.fields.pop(field_name)

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class CreateUserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ['password']
        read_only_fields = ['id', 'account_created', 'account_updated']

    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user

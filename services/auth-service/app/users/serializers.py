from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles new user registration.
    Validates password strength and creates the user.
    """
    password  = serializers.CharField(
        write_only=True,       # never returned in responses
        required=True,
        validators=[validate_password],  # Django's built-in strength checks
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label='Confirm password',
    )

    class Meta:
        model  = User
        fields = ('email', 'username', 'password', 'password2', 'role', 'grade', 'subject')

    def validate(self, data):
        # Check both passwords match
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                'password': 'Passwords do not match.'
            })
        # Students must have a grade
        if data.get('role') == 'student' and not data.get('grade'):
            raise serializers.ValidationError({
                'grade': 'Grade is required for students.'
            })
        # Teachers must have a subject
        if data.get('role') == 'teacher' and not data.get('subject'):
            raise serializers.ValidationError({
                'subject': 'Subject is required for teachers.'
            })
        return data

    def create(self, validated_data):
        # Remove password2 — not a model field
        validated_data.pop('password2')
        password = validated_data.pop('password')

        # create_user hashes the password — never store plain text
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for returning user profile data.
    Never exposes the password.
    """
    class Meta:
        model  = User
        fields = ('id', 'email', 'username', 'role', 'grade', 'subject', 'date_joined')
        read_only_fields = fields
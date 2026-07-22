from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from students.models import Student
from teachers.models import Teacher

from .models import User


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "role", "contact_no")


class RegisterSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["teacher", "student"])
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    contact_no = serializers.CharField(max_length=15, required=False, allow_blank=True)

    # teacher fields
    department = serializers.CharField(max_length=100, required=False, allow_blank=True)
    designation = serializers.CharField(max_length=100, required=False, allow_blank=True)
    # student fields
    university = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        validate_password(attrs["password"])

        if attrs["role"] == "teacher":
            if not attrs.get("department"):
                raise serializers.ValidationError({"department": "Required for teachers."})
        else:  # student
            if not attrs.get("university"):
                raise serializers.ValidationError({"university": "Required for students."})
            if not attrs.get("department"):
                raise serializers.ValidationError({"department": "Required for students."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        role = validated_data["role"]
        user = User(
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
            contact_no=validated_data.get("contact_no", ""),
            is_teacher=(role == "teacher"),
            is_student=(role == "student"),
        )
        user.set_password(validated_data["password"])
        user.save()

        if role == "teacher":
            Teacher.objects.create(
                user=user,
                department=validated_data.get("department", ""),
                designation=validated_data.get("designation", ""),
            )
        else:
            Student.objects.create(
                user=user,
                university=validated_data.get("university", ""),
                department=validated_data.get("department", ""),
            )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

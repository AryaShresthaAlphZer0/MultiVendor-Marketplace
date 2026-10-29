from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from .models import User, VendorProfile


class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = (
            "id",
            "shop_name",
            "description",
            "logo",
            "contact_phone",
            "is_verified",
            "created_at",
        )
        read_only_fields = ("id", "is_verified", "created_at")


class UserSerializer(serializers.ModelSerializer):
    """Read-only view of a user (used in responses)."""

    vendor_profile = VendorProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone",
            "vendor_profile",
            "created_at",
        )
        read_only_fields = fields


class UserUpdateSerializer(serializers.ModelSerializer):
    """Fields a user may change on their own account."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=User.Role.choices, default=User.Role.CUSTOMER
    )
    shop_name = serializers.CharField(
        write_only=True, required=False, allow_blank=False, max_length=120
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "phone",
            "role",
            "shop_name",
        )

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password2": "Passwords do not match."})

        validate_password(attrs["password"])

        if attrs["role"] == User.Role.VENDOR:
            shop_name = attrs.get("shop_name")
            if not shop_name:
                raise serializers.ValidationError(
                    {"shop_name": "Vendors must provide a shop name."}
                )
            if VendorProfile.objects.filter(shop_name__iexact=shop_name).exists():
                raise serializers.ValidationError(
                    {"shop_name": "This shop name is already taken."}
                )
        else:
            attrs.pop("shop_name", None)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        shop_name = validated_data.pop("shop_name", None)
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)  # hashes the password
        user.save()

        if user.role == User.Role.VENDOR:
            VendorProfile.objects.create(user=user, shop_name=shop_name)

        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        validate_password(value, self.context["request"].user)
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
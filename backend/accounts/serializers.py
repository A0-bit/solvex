from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from reports.utils import strip_exif


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label="Confirm password")

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password2", "role", "phone"]
        extra_kwargs = {
            "email": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        # Users cannot self-assign superadmin role via registration
        if validated_data.get("role") == User.Role.SUPERADMIN:
            validated_data["role"] = User.Role.USER
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError(
                {"detail": "Invalid credentials. Please try again."}
            )
        if not user.is_active:
            raise serializers.ValidationError({"detail": "This account is disabled."})

        refresh = RefreshToken.for_user(user)
        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class UserProfileSerializer(serializers.ModelSerializer):
    """Read and update own profile. Role is read-only for self-updates."""

    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "role",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["username", "role", "created_at", "updated_at"]

    def validate_avatar(self, value):
        if value:
            max_mb = 2
            if value.size > max_mb * 1024 * 1024:
                raise serializers.ValidationError(f"Avatar must be under {max_mb} MB.")
            # Strip EXIF metadata from avatar
            import io
            from django.core.files.base import ContentFile
            cleaned_bytes = strip_exif(value)
            ext = value.name.rsplit(".", 1)[-1].lower()
            return ContentFile(cleaned_bytes, name=f"avatar.{ext}")
        return value


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

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])


class AdminUserSerializer(serializers.ModelSerializer):
    """Used by SuperAdmin to view/edit any user."""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

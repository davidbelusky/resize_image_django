from rest_framework import serializers
from django.contrib.auth.password_validation import *
from django.core import exceptions as django_exceptions
from djoser.serializers import UserCreateSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Images, StyleImage, DemoStyler, User
from .validators import ImageValidators, StyleImageValidators, GeneralValidators


class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "is_active", "token")
        read_only_fields = ("id", "token")

class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        try:
            validate_password(attrs["new_password"])
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        return attrs

class UserRegisterSerializer(UserCreateSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ["email", "password"]

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Add custom fields to JWT
    Default JWT obtain only user_id
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user_details"] = {"user_id": user.id, "email": user.email}
        return token

# OTHER SERIALIZERS

class DemoStylerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemoStyler
        fields = "__all__"
        read_only_fields = ["result_image"]

class ActiveUsersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","email")

class ImageSerializer(serializers.ModelSerializer):
    """
    - img_format: fill automatically get from uploaded image
    - owner: logged user
    """

    img_format = serializers.ReadOnlyField()
    owner = serializers.ReadOnlyField(source="owner.email")
    img_name = serializers.CharField(max_length=25, allow_blank=False, allow_null=False)

    class Meta:
        model = Images
        fields = "__all__"

    def validate(self, data):
        return ImageValidators.validate_image_input(data, self.context)

    def validate_img_name(self, data):
        return GeneralValidators.unique_image_name(data, self.context)


class ImageOneSerializer(serializers.ModelSerializer):
    """
    uploaded_image and img_format cannot be edited
    """

    owner = serializers.ReadOnlyField(source="owner.email")

    class Meta:
        model = Images
        fields = "__all__"
        read_only_fields = ["uploaded_image", "img_format"]

    def validate(self, data):
        return ImageValidators.validate_image_input(data, self.context)

    def validate_img_name(self, data):
        return GeneralValidators.unique_image_one_name(data, self.context)


class StyleImageSerializer(serializers.ModelSerializer):
    """
    owner: logged user
    """

    owner = serializers.ReadOnlyField(source="owner.email")

    class Meta:
        model = StyleImage
        fields = "__all__"
        read_only_fields = ["img_format"]

    def validate_img_name(self, data):
        return GeneralValidators.unique_image_name(data, self.context)

    def validate_share_user(self, data):
        return StyleImageValidators.validate_share_user_styled_image(data, self.context)

    def validate_original_image(self, data):
        if data == None:
            raise serializers.ValidationError(
                "Please input original image for stylizing"
            )
        return StyleImageValidators.validate_owner_original_image(data, self.context)


class StyleImageOneSerializer(serializers.ModelSerializer):
    """
    - owner: logged user
    """

    owner = serializers.ReadOnlyField(source="owner.email")

    class Meta:
        model = StyleImage
        fields = "__all__"
        read_only_fields = ["styled_image", "original_image", "img_format"]

    def validate_share_user_styled(self, data):
        return StyleImageValidators.validate_share_user_styled_image(data, self.context)

    def validate_img_name(self, data):
        return GeneralValidators.unique_image_one_name(data, self.context)

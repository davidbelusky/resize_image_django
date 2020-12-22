from rest_framework import serializers
from django.contrib.auth.password_validation import *

from django.contrib.auth.models import User
from .models import Images, StyleImage, DemoStyler
from .validators import ImageValidators, StyleImageValidators, GeneralValidators


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


    def validate_password(self, password):
        """
        Validate password:
        - min length = 5
        - password cannot be common
        - password cannot obtain only numbers
        - password and password2 input must matching
        """
        try:
            validate_password(password)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))

        return password

class DemoStylerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemoStyler
        fields = "__all__"
        read_only_fields = ["result_image"]



class ImageSerializer(serializers.ModelSerializer):
    """
    - img_format: fill automatically get from uploaded image
    - owner: logged user
    """

    img_format = serializers.ReadOnlyField()
    owner = serializers.ReadOnlyField(source="owner.username")
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

    owner = serializers.ReadOnlyField(source="owner.username")

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

    owner = serializers.ReadOnlyField(source="owner.username")

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

    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = StyleImage
        fields = "__all__"
        read_only_fields = ["styled_image", "original_image", "img_format"]

    def validate_share_user_styled(self, data):
        return StyleImageValidators.validate_share_user_styled_image(data, self.context)

    def validate_img_name(self, data):
        return GeneralValidators.unique_image_one_name(data, self.context)

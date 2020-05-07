from rest_framework import serializers
from .models import Images

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import *


def validate_image_input(data,context):
    """
    - if width or height keys are missing set them to default 0
    - if width or height are not filled then set them to default 0
    - width and height must be >= then 0
    - owner cannot be in share users list
    """
    request = context['request']

    if 'width' not in data or data['width'] == '': data['width'] = 0
    if 'height' not in data or data['height'] == '': data['height'] = 0

    if int(data['width']) < 0 or int(data['height']) < 0:
        raise serializers.ValidationError('width and height must be >= 0')
    # Owner cannot be in share user list
    share_user_list_request = request.data.getlist('share_user')

    if str(request.user.id) in share_user_list_request:
        raise serializers.ValidationError(f"Owner {request.user.id} cannot be in field share_user")

    return data

class ImageSerializer(serializers.ModelSerializer):
    img_format = serializers.ReadOnlyField()
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Images
        fields = '__all__'

    def validate(self, data):
        return validate_image_input(data,self.context)

class ImageOneSerializer(serializers.ModelSerializer):
    img_format = serializers.ReadOnlyField()
    owner = serializers.ReadOnlyField(source='owner.username')
    uploaded_image = serializers.SerializerMethodField('get_image_url')
    class Meta:
        model = Images
        fields = '__all__'

    def validate(self, data):
        return validate_image_input(data, self.context)

    def get_image_url(self, obj):
        """
        Return absolute path to image
        """
        request = self.context.get('request')
        image_url = obj.uploaded_image.url
        return request.build_absolute_uri(image_url)


class UserSerializer(serializers.ModelSerializer):
    #Set style for password '*'
    password = serializers.CharField(style={'input_type':'password'},write_only=True)
    password2 = serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model = User
        fields = ['username','email','password','password2']

    def validate_password(self, value):
        """
        Validate password:
        - min length = 5
        - password cannot be common
        - password cannot obtain only numbers
        """
        try:
            validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def save(self):
        '''
        Check if password == password2
        '''
        user = User(username=self.validated_data['username'],
                    email=self.validated_data['email'])

        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'error':'Password must match'})

        user.set_password(self.validated_data['password'])
        user.save()
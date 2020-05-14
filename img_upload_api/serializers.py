from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import *

from django.contrib.auth.models import User
from .models import Images,StyleImage


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
        raise serializers.ValidationError(f"Owner {request.user} cannot be in field share_user")

    return data

class UserSerializer(serializers.ModelSerializer):
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

class ImageSerializer(serializers.ModelSerializer):
    """
    - img_format: fill automatically get from uploaded image
    - owner: logged user
    - img_name: max_length=25 ,unique
    """
    img_format = serializers.ReadOnlyField()
    owner = serializers.ReadOnlyField(source='owner.username')
    img_name = serializers.CharField(max_length=25,allow_blank=False,allow_null=False,validators=[UniqueValidator(queryset=Images.objects.all())])
    class Meta:
        model = Images
        fields = '__all__'

    def validate(self, data):
        return validate_image_input(data,self.context)

class ImageOneSerializer(serializers.ModelSerializer):
    """
    - img_format: fill automatically get from uploaded image
    - owner: logged user
    - uploaded_image if method.PUT then read only
    """
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

class StyleImageSerializer(serializers.ModelSerializer):
    """
    owner: logged user
    """
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = StyleImage
        fields = '__all__'

    def validate_share_user_styled(self,data):
        """
        - owner cannot be in share users list
        """
        request = self.context['request']
        #List of shared user.id
        shared_users = [user_id.id for user_id in data]
        if request.user.id in shared_users:
            raise serializers.ValidationError(f"Owner {request.user} cannot be in field share_user")
        return data

class StyleImageOneSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    styled_image = serializers.SerializerMethodField('get_image_url')
    class Meta:
        model = StyleImage
        fields = '__all__'

    def validate_share_user_styled(self,data):
        """
        - owner cannot be in share users list
        """
        request = self.context['request']
        #List of shared user.id
        shared_users = [user_id.id for user_id in data]
        if request.user.id in shared_users:
            raise serializers.ValidationError(f"Owner {request.user} cannot be in field share_user")
        return data

    def get_image_url(self, obj):
        """
        Return absolute path to image
        """
        request = self.context.get('request')
        image_url = obj.styled_image.url
        return request.build_absolute_uri(image_url)
from rest_framework import serializers
from .models import Images

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import *

class FileSerializer(serializers.ModelSerializer):
    img_format = serializers.ReadOnlyField()
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Images
        fields = '__all__'

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
        - length = 5
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
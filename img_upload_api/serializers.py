from rest_framework import serializers
from .models import Images

class FileSerializer(serializers.ModelSerializer):
    img_format = serializers.ReadOnlyField()
    class Meta:
        model = Images
        #fields = ['id','img_name','img_description','img_format','favourite','uploaded_image','width','height']
        fields = '__all__'

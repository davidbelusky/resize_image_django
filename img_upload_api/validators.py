from rest_framework import serializers
from .models import Images


class ImageValidators():
    @staticmethod
    def validate_image_input(data,context):
        """
        - if width or height keys are missing set them to default 0
        - if width or height are not filled then set them to default 0
        - width and height must be >= then 0
        - owner cannot be in share users list
        - img_name must be unique for logged user
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

        request = context['request']
        image_objects = Images.objects.filter(owner=request.user)
        img_names = [obj.img_name for obj in image_objects]
        if data['img_name'] in img_names:
            raise serializers.ValidationError(f'img_name: {data["img_name"]} already exist for user {request.user}')

        return data

class StyleImageValidators():
    @staticmethod
    def validate_share_user_styled_image(data,context):
        """
        - owner cannot be in share users list
        """
        request = context['request']
        # List of shared user.id
        shared_users = [user_id.id for user_id in data]
        if request.user.id in shared_users:
            raise serializers.ValidationError(f"Owner {request.user} cannot be in field share_user")
        return data

    @staticmethod
    def validate_owner_original_image(data,context):
        """
        - logged user must be owner of selected 'original_image'
        """
        orig_img_owner = data.owner
        request = context['request']
        print(orig_img_owner)
        print(request.user)
        if orig_img_owner != request.user:
            raise serializers.ValidationError(
                f'Owner of selected original_image is {orig_img_owner}.Logged user must be owner of selected original image')
        return data
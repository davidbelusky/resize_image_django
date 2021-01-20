from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from img_upload_api.models import User
from djoser import utils

def token_validate(uid: str, token: str):
    """
    Validate URL for restarting user password
    - Decode UID to user ID
    - Get user instance by user_id
    - Validate token
    Return: - False (if token is invalid)
            - user instance (if token is valid)
    """

    user_id = utils.decode_uid(uid)

    try:
        user = get_object_or_404(User, id=user_id)
    except ValueError:
        # If inputted wrong UID which is not int return response 'Invalid token'
        return False

    token_validate = default_token_generator.check_token(user, token)

    if not token_validate:
        return False
    return user
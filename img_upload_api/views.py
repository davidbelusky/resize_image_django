from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status, permissions
import django_filters.rest_framework
from rest_framework import filters
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from img_upload_api.others.helpers import token_validate
from img_upload_api.models import User
from rest_framework.permissions import IsAuthenticated

from .permissions import IsOwner
from .serializers import (
    ImageSerializer,
    ImageOneSerializer,
    StyleImageSerializer,
    StyleImageOneSerializer,
    DemoStylerSerializer,
    MyTokenObtainPairSerializer,
    PasswordResetSerializer,
    ActiveUsersListSerializer,
)
from .models import Images, StyleImage, DemoStyler



class MyTokenObtainPairView(TokenObtainPairView):
    """
    Change default generating JWT tokens (add user email to token)
    """
    serializer_class = MyTokenObtainPairSerializer



class UserPasswordResetView(APIView):
    """
    - Send link to mail for set new password
    - Input new password {"new_password":"Password123"}
    - Password was successfully changed
    - Logout user after restart password (delete auth token)
    - Link for changing password can be use only once
    """

    permission_classes = []


    def post(self, request, uid, token):
        # Validate token
        user = token_validate(uid, token)
        if not user:
            return Response({"error": "Invalid token"}, 400)

        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.data["new_password"])
        user.last_login = timezone.now()
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

class UserActivateView(APIView):
    """
    - Activate user
    """
    permission_classes = []

    def post(self, request, uid, token):
        # Validate token
        user = token_validate(uid, token)
        if not user:
            return Response({"error": "Invalid token"}, 400)
        user.is_active = True
        user.last_login = timezone.now()
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

class CheckUserActivate(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self,request):
        email = request.data['email']
        user = get_object_or_404(User, email=email)

        return Response({"user_is_active":user.is_active})

class ActiveUsersListView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    queryset = User.objects.all()
    serializer_class = ActiveUsersListSerializer

    def get_queryset(self):
        """
        Filter only active users
        """
        active_users = User.objects.filter().exclude(email=self.request.user).exclude(is_active=False)
        return active_users


class DemoStylerView(generics.CreateAPIView):
    serializer_class = DemoStylerSerializer
    queryset = DemoStyler.objects.all()
    permission_classes = []
    authentication_classes = []
    def create(self, request, *args, **kwargs):
        serializer = DemoStylerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            img_absolute_path = request.build_absolute_uri(
                serializer.data["original_image"]
            )
            styled_img_absolute_path = request.build_absolute_uri(
                serializer.data["style_image"]
            )
            # Show absolute path of uploaded_image after being created
            response_data = serializer.data
            response_data["original_image"] = img_absolute_path
            response_data["style_image"] = styled_img_absolute_path
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DemoStylerJob(generics.RetrieveAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = DemoStyler.objects.all()
    serializer_class = DemoStylerSerializer
    lookup_field = 'pk'


class ImageUploadView(generics.ListCreateAPIView):
    parser_classes = (
        MultiPartParser,
        JSONParser,
    )
    queryset = Images.objects.all()
    serializer_class = ImageSerializer
    authentication_classes = [JWTAuthentication,]
    permission_classes = [IsAuthenticated,]
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
    ]
    filterset_fields = {
        "id": ["exact"],
        "img_name": ["iexact"],
        "img_description": ["iexact"],
        "img_format": ["iexact"],
        "favourite": ["exact"],
        "created_date": ["exact", "lte", "gte"],
    }
    search_fields = [
        "img_name",
    ]

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = ImageSerializer(
            data=data, context={"request": request, "img_type": "basic"}
        )
        if serializer.is_valid():
            serializer.save(owner=self.request.user)
            img_absolute_path = request.build_absolute_uri(
                serializer.data["uploaded_image"]
            )
            # Show absolute path of uploaded_image after being created
            response_data = serializer.data
            response_data["uploaded_image"] = img_absolute_path
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        """
        Filter only images for logged user
        """
        user_images = Images.objects.filter(owner=self.request.user)
        return user_images


class ImageOneView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Images.objects.all()
    serializer_class = ImageOneSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_serializer_context(self):
        """
        - send request to serializer as context
        """
        return {"request": self.request, "pk": self.kwargs["pk"], "img_type": "basic"}


class StyleImageView(generics.ListCreateAPIView):
    parser_classes = (
        MultiPartParser,
        JSONParser,
    )
    queryset = StyleImage
    serializer_class = StyleImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
    ]
    filterset_fields = {
        "id": ["exact"],
        "img_name": ["iexact"],
        "img_description": ["iexact"],
        "img_format": ["iexact"],
        "favourite": ["exact"],
        "created_date": ["exact", "lte", "gte"],
    }
    search_fields = [
        "img_name",
    ]

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = StyleImageSerializer(
            data=data, context={"request": request, "img_type": "styled"}
        )
        if serializer.is_valid():
            serializer.save(owner=self.request.user)
            response_data = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        """
        Filter only images for logged owner
        """
        user_images = StyleImage.objects.filter(owner=self.request.user)
        return user_images


class StyleImageViewOne(generics.RetrieveUpdateDestroyAPIView):
    queryset = StyleImage.objects.all()
    serializer_class = StyleImageOneSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_serializer_context(self):
        """
        - send request to serializer as context
        """
        return {"request": self.request, "pk": self.kwargs["pk"], "img_type": "styled"}


class SharedImagesView(generics.ListAPIView):
    queryset = Images.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Get shared images and styled images for logged user
        """
        # get basic shared images
        shared_images = self.request.user.shared_user.all()
        serializer_images = ImageSerializer(
            shared_images, many=True, context={"request": self.request}
        )
        # get styled share images
        shared_styled_images = self.request.user.shared_user_styled.all()
        serializer_styled_images = StyleImageSerializer(
            shared_styled_images, many=True, context={"request": self.request}
        )
        # all shared images
        shared_images = {
            "images": serializer_images.data,
            "styled_images": serializer_styled_images.data,
        }
        return Response(shared_images, status.HTTP_200_OK)


class FavouriteImagesView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Show basic images and styled images where
        - logged user = owner and favourite = True
        """
        # Styled images
        styled_images = StyleImage.objects.filter(
            owner=self.request.user, favourite=True
        )
        serializer_style = StyleImageSerializer(
            styled_images, many=True, context={"request": self.request}
        )
        # Basic images
        images = Images.objects.filter(owner=self.request.user, favourite=True)
        serializer_images = ImageSerializer(
            images, many=True, context={"request": self.request}
        )
        # styled + basic images
        favourite_images = {
            "images": serializer_images.data,
            "styled_images": serializer_style.data,
        }
        return Response(favourite_images, status.HTTP_200_OK)

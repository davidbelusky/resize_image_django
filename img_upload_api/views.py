from rest_framework.parsers import MultiPartParser,JSONParser
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status,permissions
from django.contrib.auth.models import User
import django_filters.rest_framework
from rest_framework import filters

from .permissions import IsOwner
from .serializers import ImageSerializer,ImageOneSerializer,UserSerializer
from .models import Images

class RegisterUser(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ImageUploadView(generics.ListCreateAPIView):
    parser_classes = (MultiPartParser,JSONParser,)
    queryset = Images.objects.all()
    serializer_class = ImageSerializer
    filter_backends = [filters.SearchFilter,django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = {
            'id':['exact'],
            'img_name':['iexact'],
            'img_description':['iexact'],
            'img_format': ['iexact'],
            'favourite':['exact'],
            'created_date':['exact','lte','gte']
        }
    search_fields = ['img_name',]
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def create(self, request, *args, **kwargs):
        """
        - if width or height keys are missing set them to default 0
        - if width or height are not filled then set them to default 0
        - width and height must be >= then 0
        """
        data = request.data

        serializer = ImageSerializer(data=data,context={'request':request})

        if serializer.is_valid():
            serializer.save(owner=self.request.user)
            img_absolute_path = request.build_absolute_uri(serializer.data['uploaded_image'])
            #Show absolute path of uploaded_image after being created
            response_data = serializer.data
            response_data['uploaded_image'] = img_absolute_path
            return Response(response_data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        """
        Filter only images for logged owner
        """
        user_images = Images.objects.filter(owner=self.request.user)
        return user_images

class ImageOneView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Images.objects.all()
    serializer_class = ImageOneSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_serializer_context(self):
        """
        - Send context with request to ImageOneSerializer
        - ImageOneSerializer get from request path to 'uploaded_image' and create absolute path of image
        """
        return {
            'request':self.request
        }

class SharedImagesView(generics.ListAPIView):
    queryset = Images.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        - Show images which are shared with logged user
        """
        shared_images = self.request.user.shared_user.all()
        return shared_images

class FavouriteImagesView(generics.ListAPIView):
    queryset = Images.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated,IsOwner]

    def get_queryset(self):
        """
        Show images where
        - logged user = owner and favourite = True
        """
        favourite_images = Images.objects.filter(owner=self.request.user,favourite=True)
        return favourite_images
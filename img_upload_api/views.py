from rest_framework.parsers import MultiPartParser,JSONParser
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status,permissions
from django.contrib.auth.models import User
import django_filters.rest_framework
from rest_framework import filters

from .permissions import IsOwner
from .serializers import ImageSerializer,ImageOneSerializer,UserSerializer,StyleImageSerializer,StyleImageOneSerializer
from .models import Images,StyleImage

class RegisterUser(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ImageUploadView(generics.ListCreateAPIView):
    parser_classes = (MultiPartParser,JSONParser,)
    queryset = Images.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]
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

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = ImageSerializer(data=data,context={'request':request,
                                                        'img_type':'basic'})
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
        return {
            'request':self.request,
            'pk':self.kwargs['pk'],
            'img_type':'basic'
        }

class StyleImageView(generics.ListCreateAPIView):
    parser_classes = (MultiPartParser, JSONParser,)
    queryset = StyleImage
    serializer_class = StyleImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = {
        'id': ['exact'],
        'img_name': ['iexact'],
        'img_description': ['iexact'],
        'img_format': ['iexact'],
        'favourite': ['exact'],
        'created_date': ['exact', 'lte', 'gte']
    }
    search_fields = ['img_name', ]

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = StyleImageSerializer(data=data,context={'request':request,
                                                            'img_type':'styled'})
        if serializer.is_valid():
            serializer.save(owner=self.request.user)
            response_data = serializer.data
            return Response(response_data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

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
        return {
            'request': self.request,
            'pk':self.kwargs['pk'],
            'img_type':'styled'
        }

class SharedImagesView(generics.ListAPIView):
    queryset = Images.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Get shared images and styled images for logged user
        """
        #get basic shared images
        shared_images = self.request.user.shared_user.all()
        serializer_images = ImageSerializer(shared_images,many=True,context={'request':self.request})
        #get styled share images
        shared_styled_images = self.request.user.shared_user_styled.all()
        serializer_styled_images = StyleImageSerializer(shared_styled_images,many=True,context={'request':self.request})
        #all shared images
        shared_images = {'images':serializer_images.data,'styled_images':serializer_styled_images.data}
        return Response(shared_images,status.HTTP_200_OK)

class FavouriteImagesView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Show basic images and styled images where
        - logged user = owner and favourite = True
        """
        #Styled images
        styled_images = StyleImage.objects.filter(owner=self.request.user,favourite=True)
        serializer_style = StyleImageSerializer(styled_images,many=True,context={'request':self.request})
        #Basic images
        images = Images.objects.filter(owner=self.request.user,favourite=True)
        serializer_images = ImageSerializer(images,many=True,context={'request':self.request})
        #styled + basic images
        favourite_images = {'images':serializer_images.data,'styled_images':serializer_style.data}
        return Response(favourite_images,status.HTTP_200_OK)

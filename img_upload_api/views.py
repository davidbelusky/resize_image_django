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

        if 'width' not in data or data['width'] == '': data['width'] = 0
        if 'height' not in data or data['height'] == '': data['height'] = 0


        if int(data['width']) < 0 or int(data['height']) < 0:

            return Response({'error':'width and height must be >= 0'})

        #'owner' cannot be in 'share_user' field
        if str(request.user.id) in data.getlist('share_user'):
            return Response({'error': f'owner {request.user} cannot be inputted also in share_user'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = ImageSerializer(data=data)

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
        - Show only images which are shared with logged user
        """

        shared_images = self.request.user.shared_user.all()
        return shared_images
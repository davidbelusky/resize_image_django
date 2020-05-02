from rest_framework.parsers import MultiPartParser,JSONParser
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status,permissions
from django.contrib.auth.models import User

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
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def create(self, request, *args, **kwargs):
        """
        - if width or height keys are missing set them to default 0
        - if width or height are not filled then set them to default 0
        - width and height must be >= then 0
        """

        if 'width' not in request.data or request.data['width'] == '': request.data['width'] = 0
        if 'height' not in request.data or request.data['height'] == '': request.data['height'] = 0

        if int(request.data['width']) < 0 or int(request.data['height']) < 0:
            return Response({'error':'width and height must be >= 0'})

        data = request.data
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

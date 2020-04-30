from rest_framework.parsers import MultiPartParser,JSONParser
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status


from .serializers import FileSerializer
from .models import Images


class FileUploadView(generics.ListCreateAPIView):
    parser_classes = (MultiPartParser,JSONParser,)
    queryset = Images.objects.all()
    serializer_class = FileSerializer


    def create(self, request, *args, **kwargs):
        """
        - if width or height keys missing set them to default 0
        - if width or height are not filled then set them to default 0
        - width and height must be >= then 0
        """

        if 'width' not in request.data or request.data['width'] == '': request.data['width'] = 0
        if 'height' not in request.data or request.data['height'] == '': request.data['height'] = 0

        if int(request.data['width']) < 0 or int(request.data['height']) < 0:
            return Response({'error':'width and height must be >= 0'})

        data = request.data
        serializer = FileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


from django.urls import path,include
from . import views

urlpatterns = [
    path('uploads/',views.FileUploadView.as_view(),name='fileupload'),
    path('api-auth/register/', views.RegisterUser.as_view(),name='register_user'),
    path('api-auth/',include('rest_framework.urls')),
]
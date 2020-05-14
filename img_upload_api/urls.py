from django.urls import path,include
from . import views

urlpatterns = [
    path('uploads/',views.ImageUploadView.as_view(),name='fileupload'),
    path('uploads/<int:pk>',views.ImageOneView.as_view(),name='fileupload_one'),
    path('shared_images/',views.SharedImagesView.as_view(),name='shared_img'),
    path('favourites/',views.FavouriteImagesView.as_view(),name='favourite_img'),
    path('styled_images/', views.StyleImageView.as_view(), name='styled_images'),
    path('styled_images/<int:pk>',views.StyleImageViewOne.as_view(),name='styled_image_one'),
    path('api-auth/register/', views.RegisterUser.as_view(),name='register_user'),
    path('api-auth/',include('rest_framework.urls')),
]
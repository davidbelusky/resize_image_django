from django.urls import path, include
from . import views

urlpatterns = [
    path("images/", views.ImageUploadView.as_view(), name="fileupload"),
    path("images/<int:pk>", views.ImageOneView.as_view(), name="fileupload_one"),
    path("styled_images/", views.StyleImageView.as_view(), name="styled_images"),
    path(
        "styled_images/<int:pk>",
        views.StyleImageViewOne.as_view(),
        name="styled_image_one",
    ),
    path("shared_images/", views.SharedImagesView.as_view(), name="shared_img"),
    path("favourites/", views.FavouriteImagesView.as_view(), name="favourite_img"),
    path("active_users/", views.ActiveUsersListView.as_view(), name="active_users"),
    path("demo_styler/", views.DemoStylerView.as_view(), name="demo_styler"),
    path("demo_styler/<int:pk>", views.DemoStylerJob.as_view(), name="demo_styler_job"),
    # overwrite djoser jwt create urls with custom JWT generate which obtain user id and user email
    path("auth/jwt/create/", views.MyTokenObtainPairView.as_view(), name="create_jwt"),
    path("auth/jwt/create", views.MyTokenObtainPairView.as_view(), name="create_jwt2"),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")), # this must be after create_jwt
    path("auth/users/confirm/reset-password/<str:uid>/<str:token>/", views.UserPasswordResetView.as_view()),
    path("auth/users/confirm/activation/<str:uid>/<str:token>/", views.UserActivateView.as_view()),
    path("activation_check/",views.CheckUserActivate.as_view())
]

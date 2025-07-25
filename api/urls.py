from django.urls import path, include

urlpatterns = [
    path("v1/", include("finances.urls")),
    path("auth/", include("users.urls")),
]

from django.urls import path, include

urlpatterns = [
    path("v1/", include("api.v1_urls")),
    path("auth/", include("users.urls")),
]

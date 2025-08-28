from django.urls import path, include

urlpatterns = [
    path("", include("finances.urls")),
    path("", include("core.urls")),
    path("", include("messaging.urls")),
]

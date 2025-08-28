from django.urls import path, include
from users.views import ProfileView

urlpatterns = [
    path("", include("finances.urls")),
    path("", include("core.urls")),
    path("", include("messaging.urls")),
    path("", include("groups.urls")),
    path("", include("buildings.urls")),
    path("", include("challenges.urls")),
    path("", include("funds.urls")),
    path("users/me/", ProfileView.as_view(), name="profile"),
]

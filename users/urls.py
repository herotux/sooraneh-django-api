from django.urls import path
from . import views

from .views import ProfileView

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("password-reset/", views.PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password-reset-confirm/", views.PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
]

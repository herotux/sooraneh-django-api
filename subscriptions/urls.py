from django.urls import path
from .views import PaymentRequestView, PaymentVerifyView

urlpatterns = [
    path('request-payment/', PaymentRequestView.as_view(), name='request-payment'),
    path('verify-payment/', PaymentVerifyView.as_view(), name='verify-payment'),
]

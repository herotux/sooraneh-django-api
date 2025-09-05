from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
import datetime
import uuid
import requests
import json
from .models import Plan, Subscription, Payment
from .serializers import PaymentRequestSerializer

# Zarinpal URLs
ZARINPAL_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZARINPAL_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZARINPAL_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
# Use sandbox URLs if in development
if settings.DEBUG:
    ZARINPAL_API_REQUEST = "https://sandbox.zarinpal.com/pg/services/WebGate/request"
    ZARINPAL_API_VERIFY = "https://sandbox.zarinpal.com/pg/services/WebGate/verify"
    ZARINPAL_API_STARTPAY = "https://sandbox.zarinpal.com/pg/StartPay/{authority}"


class PaymentRequestView(generics.GenericAPIView):
    serializer_class = PaymentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan_id = serializer.validated_data['plan_id']
        plan = get_object_or_404(Plan, id=plan_id)
        user = request.user

        payment = Payment.objects.create(
            user=user, plan=plan, amount=plan.price, status='PENDING',
            transaction_id=f"SUB_{user.id}_{uuid.uuid4()}"
        )

        req_data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": int(plan.price),
            "callback_url": request.build_absolute_uri(f"/api/v1/subscriptions/verify-payment/"),
            "description": f"Subscription to {plan.name} for {user.email}",
            "metadata": {"user_id": user.id, "plan_id": plan.id}
        }
        req_header = {"accept": "application/json", "content-type": "application/json"}

        try:
            res = requests.post(ZARINPAL_API_REQUEST, data=json.dumps(req_data), headers=req_header)
            response_data = res.json()

            if response_data['data']['code'] == 100:
                authority = response_data['data']['authority']
                payment.transaction_id = authority
                payment.save()
                payment_url = ZARINPAL_API_STARTPAY.format(authority=authority)
                return Response({'payment_url': payment_url})
            else:
                payment.status = 'FAILED'
                payment.save()
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            payment.status = 'FAILED'
            payment.save()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        authority = request.GET.get('Authority')
        status_param = request.GET.get('Status')

        if not authority or status_param != 'OK':
            return Response({'error': 'Payment was cancelled or failed.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(transaction_id=authority, status='PENDING')
        except Payment.DoesNotExist:
            return Response({'error': 'Invalid transaction.'}, status=status.HTTP_404_NOT_FOUND)

        req_header = {"accept": "application/json", "content-type": "application/json"}
        req_data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": int(payment.amount),
            "authority": authority
        }

        try:
            res = requests.post(ZARINPAL_API_VERIFY, data=json.dumps(req_data), headers=req_header)
            response_data = res.json()

            if response_data['data']['code'] == 100:
                payment.status = 'COMPLETED'
                payment.save()

                subscription, created = Subscription.objects.get_or_create(
                    user=payment.user,
                    defaults={'plan': payment.plan, 'end_date': timezone.now() + datetime.timedelta(days=payment.plan.duration_days)}
                )
                if not created:
                    subscription.plan = payment.plan
                    if subscription.end_date < timezone.now():
                        subscription.end_date = timezone.now() + datetime.timedelta(days=payment.plan.duration_days)
                    else:
                        subscription.end_date += datetime.timedelta(days=payment.plan.duration_days)
                    subscription.is_active = True
                    subscription.save()

                return Response({'status': 'Payment successful and subscription activated.'})
            else:
                payment.status = 'FAILED'
                payment.save()
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            payment.status = 'FAILED'
            payment.save()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

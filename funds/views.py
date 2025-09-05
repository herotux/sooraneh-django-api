from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Fund, FundMembership, Contribution
from .serializers import FundSerializer, ContributionSerializer, PayoutCreateSerializer
from subscriptions.permissions import HasFeaturePermission

User = get_user_model()


class FundViewSet(viewsets.ModelViewSet):
    """
    یک ViewSet برای مدیریت صندوق‌های پس‌انداز خانوادگی.
    """
    serializer_class = FundSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        کاربران فقط صندوق‌هایی را می‌بینند که در آن عضو هستند.
        """
        return Fund.objects.filter(memberships__user=self.request.user)

    def perform_create(self, serializer):
        """
        هنگام ایجاد صندوق، کاربر فعلی به عنوان سازنده و اولین عضو ثبت می‌شود.
        """
        fund = serializer.save(creator=self.request.user)
        FundMembership.objects.create(fund=fund, user=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated, HasFeaturePermission.for_feature('can_create_funds')]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """
        یک کاربر دیگر را به صندوق دعوت می‌کند.
        فقط سازنده صندوق می‌تواند دیگران را دعوت کند.
        Body: `{"user_id": <user_id>}`
        """
        fund = self.get_object()
        if fund.creator != request.user:
            return Response(
                {'error': 'Only the creator of the fund can invite others.'},
                status=status.HTTP_403_FORBIDDEN
            )

        user_id = request.data.get('user_id')
        try:
            user_to_invite = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        membership, created = FundMembership.objects.get_or_create(
            fund=fund,
            user=user_to_invite
        )

        if not created:
            return Response({'status': 'user already in fund'}, status=status.HTTP_200_OK)

        return Response({'status': 'user invited to fund'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def contribute(self, request, pk=None):
        """
        یک عضو، پرداخت سهم خود را برای یک دوره ثبت می‌کند.
        Body: `{"contribution_date": "YYYY-MM-DD"}`
        """
        fund = self.get_object()
        try:
            membership = FundMembership.objects.get(fund=fund, user=request.user)
        except FundMembership.DoesNotExist:
            return Response({'error': 'You are not a member of this fund.'}, status=status.HTTP_403_FORBIDDEN)

        contribution_date = request.data.get('contribution_date')
        if not contribution_date:
            return Response({'error': 'contribution_date is required.'}, status=status.HTTP_400_BAD_REQUEST)

        contribution = Contribution.objects.create(
            membership=membership,
            contribution_date=contribution_date,
            amount_paid=fund.contribution_amount
        )
        serializer = ContributionSerializer(contribution)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='log-payout')
    def log_payout(self, request, pk=None):
        """
        مدیر صندوق، دریافت کننده قرعه این ماه را ثبت می‌کند.
        """
        fund = self.get_object()
        if fund.creator != request.user:
            return Response(
                {'error': 'Only the creator of the fund can log payouts.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PayoutCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            recipient_membership = FundMembership.objects.get(
                id=data['recipient_membership_id'],
                fund=fund
            )
        except FundMembership.DoesNotExist:
            return Response({'error': 'Membership not found in this fund.'}, status=status.HTTP_404_NOT_FOUND)

        payout_amount = fund.contribution_amount * fund.memberships.count()

        payout = Payout.objects.create(
            fund=fund,
            recipient=recipient_membership,
            payout_date=data['payout_date'],
            amount=payout_amount
        )

        # Using the read-serializer for the response
        from .serializers import PayoutSerializer
        return Response(PayoutSerializer(payout).data, status=status.HTTP_201_CREATED)

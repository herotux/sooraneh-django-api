from rest_framework import serializers
from .models import Fund, FundMembership, Contribution, Payout
from users.serializers import SimpleUserSerializer


class FundMembershipSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    class Meta:
        model = FundMembership
        fields = ['id', 'user', 'join_date']


class PayoutSerializer(serializers.ModelSerializer):
    recipient = FundMembershipSerializer(read_only=True)
    class Meta:
        model = Payout
        fields = ['id', 'recipient', 'payout_date', 'amount']


class FundSerializer(serializers.ModelSerializer):
    creator = SimpleUserSerializer(read_only=True)
    memberships = FundMembershipSerializer(many=True, read_only=True)
    payouts = PayoutSerializer(many=True, read_only=True)

    class Meta:
        model = Fund
        fields = [
            'id', 'name', 'creator', 'contribution_amount', 'start_date',
            'payout_frequency_days', 'memberships', 'payouts'
        ]
        read_only_fields = ['creator']


class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = ['id', 'membership', 'contribution_date', 'amount_paid', 'payment_date']


class PayoutCreateSerializer(serializers.Serializer):
    recipient_membership_id = serializers.IntegerField()
    payout_date = serializers.DateField()

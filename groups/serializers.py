from rest_framework import serializers
from .models import Group, GroupExpense, Split
from users.serializers import SimpleUserSerializer
from django.db import transaction

class GroupSerializer(serializers.ModelSerializer):
    owner = SimpleUserSerializer(read_only=True)
    members = SimpleUserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'owner', 'members', 'created_at']
        read_only_fields = ['owner']


class SplitSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Split
        fields = ['user', 'amount_owed']


class ManualSplitSerializer(serializers.Serializer):
    """
    Serializer for a single user's split in a manual split.
    """
    user_id = serializers.IntegerField()
    amount_owed = serializers.DecimalField(max_digits=10, decimal_places=2)


class GroupExpenseSerializer(serializers.ModelSerializer):
    splits = SplitSerializer(many=True, read_only=True)
    payer = SimpleUserSerializer(read_only=True)
    # Write-only fields for creation
    payer_id = serializers.IntegerField(write_only=True)
    split_type = serializers.ChoiceField(choices=['EQUAL', 'MANUAL'], write_only=True)
    manual_splits = ManualSplitSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = GroupExpense
        fields = [
            'id', 'description', 'amount', 'payer', 'date',
            'splits', 'payer_id', 'split_type', 'manual_splits'
        ]

    def validate(self, data):
        if data['split_type'] == 'MANUAL':
            if 'manual_splits' not in data or not data['manual_splits']:
                raise serializers.ValidationError("For a 'MANUAL' split, 'manual_splits' field is required.")

            total_split_amount = sum(item['amount_owed'] for item in data['manual_splits'])
            if total_split_amount != data['amount']:
                raise serializers.ValidationError("The sum of manual splits must equal the total expense amount.")
        return data

    def create(self, validated_data):
        group = self.context['group']
        payer_id = validated_data.pop('payer_id')
        split_type = validated_data.pop('split_type')
        manual_splits_data = validated_data.pop('manual_splits', None)

        with transaction.atomic():
            expense = GroupExpense.objects.create(group=group, payer_id=payer_id, **validated_data)

            if split_type == 'EQUAL':
                member_count = group.members.count()
                if member_count == 0:
                    raise serializers.ValidationError("Cannot split expense in a group with no members.")
                amount_per_member = expense.amount / member_count
                for member in group.members.all():
                    Split.objects.create(expense=expense, user=member, amount_owed=amount_per_member)

            elif split_type == 'MANUAL':
                for split_data in manual_splits_data:
                    Split.objects.create(expense=expense, **split_data)

        return expense

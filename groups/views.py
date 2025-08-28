from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Sum
from collections import defaultdict
from decimal import Decimal
from .models import Group, GroupExpense, Split
from .serializers import GroupSerializer, GroupExpenseSerializer
from django.shortcuts import get_object_or_404

User = get_user_model()


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see groups they are a member of
        return self.request.user.expense_groups.all()

    def perform_create(self, serializer):
        # Set the owner and add them as the first member
        group = serializer.save(owner=self.request.user)
        group.members.add(self.request.user)

    @action(detail=True, methods=['post'], url_path='add-member')
    def add_member(self, request, pk=None):
        group = self.get_object()
        # Only the owner can add members
        if group.owner != request.user:
            return Response({'error': 'Only the group owner can add members.'}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        try:
            user_to_add = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        group.members.add(user_to_add)
        return Response({'status': 'member added'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='remove-member')
    def remove_member(self, request, pk=None):
        group = self.get_object()
        # Only the owner can remove members
        if group.owner != request.user:
            return Response({'error': 'Only the group owner can remove members.'}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        try:
            user_to_remove = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if user_to_remove == group.owner:
            return Response({'error': 'The group owner cannot be removed.'}, status=status.HTTP_400_BAD_REQUEST)

        group.members.remove(user_to_remove)
        return Response({'status': 'member removed'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        group = self.get_object()
        user = request.user

        # Check if user is in the group
        if user not in group.members.all():
            return Response({'error': 'You are not a member of this group.'}, status=status.HTTP_403_FORBIDDEN)

        # Calculate total paid by each member
        total_paid = defaultdict(Decimal)
        for expense in group.expenses.all():
            total_paid[expense.payer_id] += expense.amount

        # Calculate total owed by each member
        total_owed = defaultdict(Decimal)
        for split in Split.objects.filter(expense__group=group):
            total_owed[split.user_id] += split.amount_owed

        # Calculate net balance for each member
        balances = defaultdict(Decimal)
        for member in group.members.all():
            balances[member.id] = total_paid[member.id] - total_owed[member.id]

        # Simplify debts and credits
        creditors = {uid: bal for uid, bal in balances.items() if bal > 0}
        debtors = {uid: bal for uid, bal in balances.items() if bal < 0}

        settlements = []

        # This is a simplified settlement algorithm. A more robust one would be needed for complex cases.
        for debtor_id, debtor_balance in debtors.items():
            amount_to_settle = abs(debtor_balance)
            for creditor_id, creditor_balance in creditors.items():
                if amount_to_settle == 0: break

                can_settle = min(amount_to_settle, creditor_balance)
                settlements.append({
                    'from': User.objects.get(id=debtor_id).username,
                    'to': User.objects.get(id=creditor_id).username,
                    'amount': can_settle
                })

                amount_to_settle -= can_settle
                creditors[creditor_id] -= can_settle

        return Response({
            'user_balance': balances[user.id],
            'balances': balances,
            'settlements': settlements,
        })


class GroupExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = GroupExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter expenses based on the group_pk from the URL
        group_pk = self.kwargs.get('group_pk')
        group = get_object_or_404(self.request.user.expense_groups, pk=group_pk)
        return GroupExpense.objects.filter(group=group)

    def get_serializer_context(self):
        # Pass group to the serializer context
        context = super().get_serializer_context()
        context['group'] = get_object_or_404(
            self.request.user.expense_groups,
            pk=self.kwargs.get('group_pk')
        )
        return context

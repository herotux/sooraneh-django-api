# finances/views.py
from rest_framework import viewsets, permissions
from .models import (
    Person,
    Category,
    Tag,
    Budget,
    Income,
    Expense,
    Debt,
    Credit,
    Installment,
    Wallet,
)
from .serializers import (
    PersonSerializer,
    CategorySerializer,
    TagSerializer,
    BudgetSerializer,
    IncomeSerializer,
    ExpenseSerializer,
    DebtSerializer,
    CreditSerializer,
    InstallmentSerializer,
    WalletSerializer,
)

class PersonViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PersonSerializer
    queryset = None  # ⚠️ این خط رو حتماً بزنید

    def get_queryset(self):
        return Person.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = None

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TagSerializer
    queryset = None

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BudgetSerializer
    queryset = None

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IncomeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = IncomeSerializer
    queryset = None

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        wallet = serializer.validated_data.get('wallet')
        amount = serializer.validated_data.get('amount')

        if wallet:
            wallet.balance += amount
            wallet.save()

        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.instance
        original_amount = instance.amount
        original_wallet = instance.wallet

        new_wallet = serializer.validated_data.get('wallet', original_wallet)
        new_amount = serializer.validated_data.get('amount', original_amount)

        if original_wallet == new_wallet:
            if original_wallet:
                balance_change = new_amount - original_amount
                original_wallet.balance += balance_change
                original_wallet.save()
        else:
            if original_wallet:
                original_wallet.balance -= original_amount
                original_wallet.save()
            if new_wallet:
                new_wallet.balance += new_amount
                new_wallet.save()

        serializer.save()

    def perform_destroy(self, instance):
        if instance.wallet:
            instance.wallet.balance -= instance.amount
            instance.wallet.save()

        instance.delete()


from rest_framework.exceptions import ValidationError

class ExpenseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExpenseSerializer
    queryset = None

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        wallet = serializer.validated_data.get('wallet')
        amount = serializer.validated_data.get('amount')

        if wallet:
            if wallet.balance < amount:
                raise ValidationError(f"Insufficient balance in wallet '{wallet.name}'.")
            wallet.balance -= amount
            wallet.save()

        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.instance
        original_amount = instance.amount
        original_wallet = instance.wallet

        # Get the new data from the serializer
        new_wallet = serializer.validated_data.get('wallet', original_wallet)
        new_amount = serializer.validated_data.get('amount', original_amount)

        # Case 1: Wallet is unchanged
        if original_wallet == new_wallet:
            if original_wallet:
                # Calculate the difference in amount and adjust the balance
                balance_change = original_amount - new_amount
                # Check for sufficient funds if the expense increases
                if balance_change < 0 and original_wallet.balance < abs(balance_change):
                     raise ValidationError(f"Insufficient balance in wallet '{original_wallet.name}' to cover the increased expense.")
                original_wallet.balance += balance_change
                original_wallet.save()
        # Case 2: Wallet has changed
        else:
            # Step 2.1: Revert the amount from the original wallet
            if original_wallet:
                original_wallet.balance += original_amount
                original_wallet.save()
            # Step 2.2: Deduct the new amount from the new wallet
            if new_wallet:
                if new_wallet.balance < new_amount:
                    # This check is important. We should revert the change on the original wallet if this fails.
                    # For simplicity, we raise an error. A more robust solution might use transactions.
                    if original_wallet:
                        original_wallet.balance -= original_amount
                        original_wallet.save()
                    raise ValidationError(f"Insufficient balance in new wallet '{new_wallet.name}'.")
                new_wallet.balance -= new_amount
                new_wallet.save()

        serializer.save()

    def perform_destroy(self, instance):
        # If the expense had a wallet, add the amount back to its balance
        if instance.wallet:
            instance.wallet.balance += instance.amount
            instance.wallet.save()

        instance.delete()


class DebtViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DebtSerializer
    queryset = None

    def get_queryset(self):
        return Debt.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CreditViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreditSerializer
    queryset = None

    def get_queryset(self):
        return Credit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InstallmentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InstallmentSerializer
    queryset = None

    def get_queryset(self):
        return Installment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WalletViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WalletSerializer
    queryset = None

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# finances/serializers.py
from rest_framework import serializers
from .models import *

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        exclude = ['user']

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True, source='parent')

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent_id', 'is_income', 'children']

    def get_children(self, obj):
        # Recursively serialize children
        children = Category.objects.filter(parent=obj)
        serializer = CategorySerializer(children, many=True)
        return serializer.data

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        exclude = ['user']

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        exclude = ['user']


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        exclude = ['user']


class IncomeSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    person_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    wallet = WalletSerializer(read_only=True)
    wallet_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    class Meta:
        model = Income
        exclude = ['user']

class ExpenseSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    person_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    wallet = WalletSerializer(read_only=True)
    wallet_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    class Meta:
        model = Expense
        exclude = ['user']

class DebtSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    person_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Debt
        exclude = ['user']

class CreditSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    person_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Credit
        exclude = ['user']

class InstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installment
        exclude = ['user']

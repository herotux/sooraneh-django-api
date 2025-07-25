# finances/serializers.py
from rest_framework import serializers
from .models import *

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        exclude = ['user']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ['user']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        exclude = ['user']

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        exclude = ['user']

class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        exclude = ['user']

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        exclude = ['user']

class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        exclude = ['user']

class CreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credit
        exclude = ['user']

class InstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installment
        exclude = ['user']

from rest_framework import serializers
from .models import TodoList, TodoItem, ShoppingList, ShoppingItem
from users.serializers import SimpleUserSerializer


class TodoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoItem
        fields = ['id', 'text', 'completed', 'created_at']


class TodoListSerializer(serializers.ModelSerializer):
    items = TodoItemSerializer(many=True, read_only=True)
    user = SimpleUserSerializer(read_only=True)
    shared_with = SimpleUserSerializer(many=True, read_only=True)

    class Meta:
        model = TodoList
        fields = ['id', 'name', 'is_archived', 'user', 'shared_with', 'items']
        read_only_fields = ['user']


class ShoppingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingItem
        fields = ['id', 'name', 'quantity', 'purchased', 'created_at']


class ShoppingListSerializer(serializers.ModelSerializer):
    items = ShoppingItemSerializer(many=True, read_only=True)
    user = SimpleUserSerializer(read_only=True)
    shared_with = SimpleUserSerializer(many=True, read_only=True)

    class Meta:
        model = ShoppingList
        fields = ['id', 'name', 'is_archived', 'user', 'shared_with', 'items']
        read_only_fields = ['user']

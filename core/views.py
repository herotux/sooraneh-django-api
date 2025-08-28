from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import TodoList, TodoItem, ShoppingList, ShoppingItem
from .serializers import (
    TodoListSerializer,
    TodoItemSerializer,
    ShoppingListSerializer,
    ShoppingItemSerializer,
)
from django.shortcuts import get_object_or_404

User = get_user_model()


class TodoListViewSet(viewsets.ModelViewSet):
    serializer_class = TodoListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = TodoList.objects.filter(Q(user=user) | Q(shared_with=user)).distinct()

        # Filter by archive status
        is_archived_query = self.request.query_params.get('archived', 'false').lower()
        if is_archived_query == 'true':
            return qs.filter(is_archived=True)
        return qs.filter(is_archived=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        todolist = self.get_object()
        if todolist.user != request.user:
            return Response({'error': 'You can only share lists you own.'}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        try:
            user_to_share_with = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        todolist.shared_with.add(user_to_share_with)
        return Response({'status': 'list shared'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        todolist = self.get_object()
        if todolist.user != request.user:
            return Response({'error': 'You can only archive lists you own.'}, status=status.HTTP_403_FORBIDDEN)

        todolist.is_archived = not todolist.is_archived
        todolist.save()
        return Response({'status': f"list {'archived' if todolist.is_archived else 'unarchived'}"})


class TodoItemViewSet(viewsets.ModelViewSet):
    serializer_class = TodoItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        todolist_pk = self.kwargs.get('todolist_pk')
        todolist = get_object_or_404(
            TodoList.objects.filter(Q(user=self.request.user) | Q(shared_with=self.request.user)),
            pk=todolist_pk
        )
        return TodoItem.objects.filter(todolist=todolist)

    def perform_create(self, serializer):
        todolist_pk = self.kwargs.get('todolist_pk')
        todolist = get_object_or_404(
            TodoList.objects.filter(Q(user=self.request.user) | Q(shared_with=self.request.user)),
            pk=todolist_pk
        )
        serializer.save(todolist=todolist)


class ShoppingListViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = ShoppingList.objects.filter(Q(user=user) | Q(shared_with=user)).distinct()

        is_archived_query = self.request.query_params.get('archived', 'false').lower()
        if is_archived_query == 'true':
            return qs.filter(is_archived=True)
        return qs.filter(is_archived=False)


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        shoppinglist = self.get_object()
        if shoppinglist.user != request.user:
            return Response({'error': 'You can only share lists you own.'}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        try:
            user_to_share_with = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        shoppinglist.shared_with.add(user_to_share_with)
        return Response({'status': 'list shared'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        shoppinglist = self.get_object()
        if shoppinglist.user != request.user:
            return Response({'error': 'You can only archive lists you own.'}, status=status.HTTP_403_FORBIDDEN)

        shoppinglist.is_archived = not shoppinglist.is_archived
        shoppinglist.save()
        return Response({'status': f"list {'archived' if shoppinglist.is_archived else 'unarchived'}"})


class ShoppingItemViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        shoppinglist_pk = self.kwargs.get('shoppinglist_pk')
        shoppinglist = get_object_or_404(
            ShoppingList.objects.filter(Q(user=self.request.user) | Q(shared_with=self.request.user)),
            pk=shoppinglist_pk
        )
        return ShoppingItem.objects.filter(shoppinglist=shoppinglist)

    def perform_create(self, serializer):
        shoppinglist_pk = self.kwargs.get('shoppinglist_pk')
        shoppinglist = get_object_or_404(
            ShoppingList.objects.filter(Q(user=self.request.user) | Q(shared_with=self.request.user)),
            pk=shoppinglist_pk
        )
        serializer.save(shoppinglist=shoppinglist)

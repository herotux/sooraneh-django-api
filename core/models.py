from django.db import models
from django.conf import settings


class TodoList(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_todolists"
    )
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="shared_todolists", blank=True
    )
    name = models.CharField(max_length=100)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class TodoItem(models.Model):
    todolist = models.ForeignKey(TodoList, on_delete=models.CASCADE, related_name="items")
    text = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['created_at']


class ShoppingList(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_shoppinglists"
    )
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="shared_shoppinglists", blank=True
    )
    name = models.CharField(max_length=100)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ShoppingItem(models.Model):
    shoppinglist = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50, blank=True, null=True) # e.g., "1kg", "2 packs"
    purchased = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['created_at']

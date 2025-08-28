from django.contrib import admin
from .models import TodoList, TodoItem, ShoppingList, ShoppingItem

admin.site.register(TodoList)
admin.site.register(TodoItem)
admin.site.register(ShoppingList)
admin.site.register(ShoppingItem)

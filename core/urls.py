from rest_framework_nested import routers
from .views import (
    TodoListViewSet,
    TodoItemViewSet,
    ShoppingListViewSet,
    ShoppingItemViewSet,
)

# Main router for top-level resources
router = routers.DefaultRouter()
router.register(r'todolists', TodoListViewSet, basename='todolist')
router.register(r'shoppinglists', ShoppingListViewSet, basename='shoppinglist')

# Nested router for todo items
todolists_router = routers.NestedDefaultRouter(router, r'todolists', lookup='todolist')
todolists_router.register(r'items', TodoItemViewSet, basename='todoitem')

# Nested router for shopping items
shoppinglists_router = routers.NestedDefaultRouter(router, r'shoppinglists', lookup='shoppinglist')
shoppinglists_router.register(r'items', ShoppingItemViewSet, basename='shoppingitem')

urlpatterns = router.urls + todolists_router.urls + shoppinglists_router.urls

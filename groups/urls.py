from rest_framework_nested import routers
from .views import GroupViewSet, GroupExpenseViewSet

router = routers.DefaultRouter()
router.register(r'groups', GroupViewSet, basename='group')

groups_router = routers.NestedDefaultRouter(router, r'groups', lookup='group')
groups_router.register(r'expenses', GroupExpenseViewSet, basename='group-expense')

urlpatterns = router.urls + groups_router.urls

from rest_framework_nested import routers
from .views import BuildingViewSet, UnitViewSet, BuildingExpenseViewSet, MaintenanceFeeViewSet

# Top-level router for buildings
router = routers.DefaultRouter()
router.register(r'buildings', BuildingViewSet, basename='building')

# Nested router for units within a building
buildings_router = routers.NestedDefaultRouter(router, r'buildings', lookup='building')
buildings_router.register(r'units', UnitViewSet, basename='building-unit')
buildings_router.register(r'expenses', BuildingExpenseViewSet, basename='building-expense')

# Nested router for maintenance fees within a unit
units_router = routers.NestedDefaultRouter(buildings_router, r'units', lookup='unit')
units_router.register(r'fees', MaintenanceFeeViewSet, basename='unit-fee')


urlpatterns = router.urls + buildings_router.urls + units_router.urls

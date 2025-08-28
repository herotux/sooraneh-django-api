from django.contrib import admin
from .models import Building, Unit, BuildingExpense, MaintenanceFee

admin.site.register(Building)
admin.site.register(Unit)
admin.site.register(BuildingExpense)
admin.site.register(MaintenanceFee)

from django.contrib import admin
from .models import Group, GroupExpense, Split

admin.site.register(Group)
admin.site.register(GroupExpense)
admin.site.register(Split)

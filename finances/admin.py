from django.contrib import admin
from .models import (
    Person,
    Category,
    Tag,
    Budget,
    Wallet,
    Income,
    Expense,
    Debt,
    Credit,
    Installment,
    InstallmentDetail,
)

admin.site.register(Person)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Budget)
admin.site.register(Wallet)
admin.site.register(Income)
admin.site.register(Expense)
admin.site.register(Debt)
admin.site.register(Credit)
admin.site.register(Installment)
admin.site.register(InstallmentDetail)

# finances/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"persons", views.PersonViewSet, basename='person')
router.register(r"categories", views.CategoryViewSet, basename='category')
router.register(r"tags", views.TagViewSet, basename='tag')
router.register(r"budgets", views.BudgetViewSet, basename='budget')
router.register(r"incomes", views.IncomeViewSet, basename='income')
router.register(r"expenses", views.ExpenseViewSet, basename='expense')
router.register(r"debts", views.DebtViewSet, basename='debt')
router.register(r"credits", views.CreditViewSet, basename='credit')
router.register(r"installments", views.InstallmentViewSet, basename='installment')

urlpatterns = [
    path("", include(router.urls)),
]

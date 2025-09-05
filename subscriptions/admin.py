from django.contrib import admin
from .models import Plan, Subscription, Payment

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'can_create_groups', 'can_create_funds', 'can_manage_buildings', 'max_wallets')
    list_filter = ('can_create_groups', 'can_create_funds', 'can_manage_buildings')
    search_fields = ('name',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'is_active')
    list_filter = ('plan', 'is_active')
    search_fields = ('user__username', 'user__email')
    autocomplete_fields = ['user', 'plan']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'plan', 'amount', 'status', 'created_at')
    list_filter = ('status', 'plan')
    search_fields = ('user__username', 'transaction_id')

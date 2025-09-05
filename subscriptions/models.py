from django.db import models
from django.conf import settings


class Plan(models.Model):
    """
    Represents a subscription plan (e.g., Free, Premium).
    """
    name = models.CharField(max_length=100, unique=True, help_text="نام پلن، مثلا: طلایی")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="قیمت پلن به صورت ماهانه")
    duration_days = models.PositiveIntegerField(default=30, help_text="مدت زمان پلن به روز")

    # Feature flags
    can_create_groups = models.BooleanField(default=False, help_text="آیا کاربر می‌تواند گروه دونگی ایجاد کند؟")
    can_create_funds = models.BooleanField(default=False, help_text="آیا کاربر می‌تواند صندوق خانوادگی ایجاد کند؟")
    can_manage_buildings = models.BooleanField(default=False, help_text="آیا کاربر می‌تواند ساختمان مدیریت کند؟")
    max_wallets = models.PositiveIntegerField(default=1, help_text="حداکثر تعداد کیف پول مجاز")

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """
    Represents a user's subscription to a plan.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT) # Don't delete a plan if users are subscribed
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s subscription to {self.plan.name}"


class Payment(models.Model):
    """
    Represents a payment transaction for a subscription.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    transaction_id = models.CharField(max_length=100, unique=True, help_text="ID from the payment gateway")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.transaction_id} by {self.user.username} for {self.amount}"

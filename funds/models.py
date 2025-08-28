from django.db import models
from django.conf import settings


class Fund(models.Model):
    """
    Represents a rotating savings and credit association (ROSCA), known as a "sandogh".
    """
    name = models.CharField(max_length=100, help_text="نام صندوق، مثلاً: صندوق خانوادگی بهار")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_funds',
        help_text="کاربری که این صندوق را ایجاد کرده است"
    )
    contribution_amount = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="مبلغ سهم هر عضو در هر دوره"
    )
    start_date = models.DateField(help_text="تاریخ شروع اولین دوره صندوق")
    payout_frequency_days = models.PositiveIntegerField(
        default=30, help_text="تعداد روزهای هر دوره پرداخت (مثلاً ۳۰ برای ماهانه)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class FundMembership(models.Model):
    """
    Links a user to a fund they are a member of.
    """
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fund_memberships'
    )
    join_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('fund', 'user')

    def __str__(self):
        return f"{self.user.username} is a member of {self.fund.name}"


class Contribution(models.Model):
    """
    Represents a single contribution payment made by a member for a specific period.
    """
    membership = models.ForeignKey(
        FundMembership,
        on_delete=models.CASCADE,
        related_name='contributions'
    )
    contribution_date = models.DateField(help_text="تاریخی که این سهم برای آن است")
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contribution by {self.membership.user.username} for {self.contribution_date}"


class Payout(models.Model):
    """
    Represents a payout of the total collected amount to one member for a specific period.
    """
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name='payouts')
    recipient = models.ForeignKey(
        FundMembership,
        on_delete=models.CASCADE,
        related_name='payouts_received'
    )
    payout_date = models.DateField(help_text="تاریخی که قرعه به نام این عضو افتاده")
    amount = models.DecimalField(
        max_digits=14, decimal_places=2, help_text="مبلغ کل پرداخت شده"
    )

    def __str__(self):
        return f"Payout to {self.recipient.user.username} on {self.payout_date}"

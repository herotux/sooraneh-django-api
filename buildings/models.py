from django.db import models
from django.conf import settings


class Building(models.Model):
    """
    Represents a building managed by a user.
    """
    name = models.CharField(
        max_length=100,
        help_text="نام ساختمان، مثلاً: ساختمان بهار"
    )
    address = models.TextField(
        help_text="آدرس کامل ساختمان"
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='managed_buildings',
        help_text="کاربری که مدیر این ساختمان است"
    )

    def __str__(self):
        return self.name


class Unit(models.Model):
    """
    Represents a single unit within a building.
    """
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name='units',
        help_text="ساختمانی که این واحد به آن تعلق دارد"
    )
    unit_number = models.CharField(
        max_length=20,
        help_text="شماره یا نام واحد، مثلاً: واحد ۵ یا پلاک ۱۰"
    )
    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resident_of',
        help_text="کاربری که ساکن این واحد است"
    )

    class Meta:
        unique_together = ('building', 'unit_number')

    def __str__(self):
        return f"{self.building.name} - واحد {self.unit_number}"


class BuildingExpense(models.Model):
    """
    Represents an expense related to a building, recorded by the manager.
    """
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name='expenses',
        help_text="ساختمانی که این هزینه برای آن ثبت شده"
    )
    description = models.CharField(
        max_length=255,
        help_text="شرح هزینه، مثلاً: هزینه تعمیر آسانسور"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="مبلغ کل هزینه"
    )
    date = models.DateField(
        help_text="تاریخ انجام هزینه"
    )

    def __str__(self):
        return f"هزینه {self.description} برای {self.building.name}"


class MaintenanceFee(models.Model):
    """
    Represents a monthly maintenance fee (sharj) for a specific unit.
    """
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='maintenance_fees',
        help_text="واحدی که این شارژ برای آن است"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="مبلغ شارژ"
    )
    due_date = models.DateField(
        help_text="تاریخ سررسید پرداخت شارژ"
    )
    is_paid = models.BooleanField(
        default=False,
        help_text="وضعیت پرداخت شارژ"
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        help_text="تاریخی که شارژ پرداخت شده است"
    )

    def __str__(self):
        return f"شارژ واحد {self.unit.unit_number} برای تاریخ {self.due_date}"

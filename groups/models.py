from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Group(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_groups'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='expense_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GroupExpense(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT, # Don't delete expense if payer is deleted
        related_name='paid_group_expenses'
    )
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Ensure the payer is a member of the group
        if self.payer not in self.group.members.all():
            raise ValidationError("The payer must be a member of the group.")

    def __str__(self):
        return f"{self.description} - {self.amount}"


class Split(models.Model):
    expense = models.ForeignKey(GroupExpense, on_delete=models.CASCADE, related_name='splits')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expense_splits'
    )
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('expense', 'user')

    def __str__(self):
        return f"{self.user} owes {self.amount_owed} for {self.expense.description}"

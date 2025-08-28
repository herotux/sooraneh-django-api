from django.db import models
from django.conf import settings
from finances.models import Category


class Challenge(models.Model):
    """
    Represents a financial challenge created by a user.
    """
    class ChallengeType(models.TextChoices):
        EXPENSE_LIMIT = 'EXPENSE_LIMIT', 'Expense Limit'
        INCOME_GOAL = 'INCOME_GOAL', 'Income Goal'
        NO_SPEND = 'NO_SPEND', 'No Spend Days'

    name = models.CharField(max_length=100, help_text="نام چالش، مثلاً: 'صرفه‌جویی در هزینه رستوران'")
    challenge_type = models.CharField(
        max_length=20,
        choices=ChallengeType.choices,
        help_text="نوع چالش: سقف هزینه، هدف درآمد، یا روزهای بدون هزینه"
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_challenges'
    )
    start_date = models.DateField()
    end_date = models.DateField()

    # Fields specific to certain challenge types
    target_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="مبلغ هدف برای چالش‌های درآمدی یا سقف هزینه"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="دسته‌بندی خاص برای چالش‌های سقف هزینه"
    )

    def __str__(self):
        return self.name


class ChallengeParticipant(models.Model):
    """
    Links a user to a challenge they are participating in.
    """
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='challenge_participations'
    )
    current_progress = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="میزان پیشرفت فعلی کاربر در چالش (مثلاً مجموع هزینه‌ها)"
    )

    class Meta:
        unique_together = ('challenge', 'user')

    def __str__(self):
        return f"{self.user.username} is participating in {self.challenge.name}"

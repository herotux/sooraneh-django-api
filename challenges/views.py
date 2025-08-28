from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Sum, Q
from .models import Challenge, ChallengeParticipant
from finances.models import Income, Expense
from messaging.models import Friendship
from .serializers import ChallengeSerializer

User = get_user_model()


class ChallengeViewSet(viewsets.ModelViewSet):
    """
    یک ViewSet برای مدیریت چالش‌های مالی.

    - **list**: چالش‌هایی را که شما در آن شرکت دارید، نمایش می‌دهد.
    - **create**: یک چالش جدید ایجاد می‌کند و شما را به عنوان اولین شرکت‌کننده اضافه می‌کند.
    - **retrieve**: جزئیات یک چالش را نمایش می‌دهد.
    - **invite**: یک دوست را به چالش دعوت می‌کند (فقط توسط سازنده چالش).
    """
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        کاربران فقط چالش‌هایی را می‌بینند که در آن شرکت دارند.
        """
        return Challenge.objects.filter(participants__user=self.request.user)

    def perform_create(self, serializer):
        """
        هنگام ایجاد چالش، کاربر فعلی به عنوان سازنده و اولین شرکت‌کننده ثبت می‌شود.
        """
        challenge = serializer.save(creator=self.request.user)
        ChallengeParticipant.objects.create(challenge=challenge, user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        جزئیات یک چالش را به همراه پیشرفت هر شرکت‌کننده نمایش می‌دهد.
        """
        challenge = self.get_object()
        serializer = self.get_serializer(challenge)
        data = serializer.data

        # Calculate and add progress for each participant
        for participant_data in data['participants']:
            user_id = participant_data['user']['id']
            user = User.objects.get(id=user_id)
            progress = self.calculate_progress(challenge, user)
            participant_data['current_progress'] = progress

        return Response(data)

    def calculate_progress(self, challenge, user):
        """
        Calculates the progress of a user for a specific challenge.
        """
        qs = None
        if challenge.challenge_type == 'EXPENSE_LIMIT':
            qs = Expense.objects.filter(
                user=user,
                date__range=[challenge.start_date, challenge.end_date]
            )
            if challenge.category:
                qs = qs.filter(category=challenge.category)

        elif challenge.challenge_type == 'INCOME_GOAL':
            qs = Income.objects.filter(
                user=user,
                date__range=[challenge.start_date, challenge.end_date]
            )

        if qs:
            total = qs.aggregate(total=Sum('amount'))['total'] or 0
            return total

        # For NO_SPEND, progress could be number of days without spending.
        # This is a simplified version that just returns 0.
        return 0

    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """
        یک دوست را به چالش دعوت می‌کند.
        فقط سازنده چالش می‌تواند دیگران را دعوت کند.
        Body: `{"user_id": <friend_user_id>}`
        """
        challenge = self.get_object()
        if challenge.creator != request.user:
            return Response(
                {'error': 'Only the creator of the challenge can invite others.'},
                status=status.HTTP_403_FORBIDDEN
            )

        user_id = request.data.get('user_id')
        try:
            user_to_invite = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the invited user is a friend of the creator.
        is_friend = Friendship.objects.filter(
            (Q(from_user=request.user, to_user=user_to_invite) |
             Q(from_user=user_to_invite, to_user=request.user)),
            status='ACCEPTED'
        ).exists()

        if not is_friend:
            return Response(
                {'error': 'You can only invite friends to a challenge.'},
                status=status.HTTP_403_FORBIDDEN
            )

        participant, created = ChallengeParticipant.objects.get_or_create(
            challenge=challenge,
            user=user_to_invite
        )

        if not created:
            return Response({'status': 'user already in challenge'}, status=status.HTTP_200_OK)

        return Response({'status': 'user invited to challenge'}, status=status.HTTP_201_CREATED)

from rest_framework import serializers
from .models import Challenge, ChallengeParticipant
from users.serializers import SimpleUserSerializer


class ChallengeParticipantSerializer(serializers.ModelSerializer):
    """
    Serializer for a participant in a challenge, showing user details.
    """
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = ChallengeParticipant
        fields = ['user', 'current_progress']


class ChallengeSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and viewing challenges.
    """
    creator = SimpleUserSerializer(read_only=True)
    participants = ChallengeParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Challenge
        fields = [
            'id', 'name', 'challenge_type', 'creator', 'start_date', 'end_date',
            'target_amount', 'category', 'participants'
        ]
        read_only_fields = ['creator']

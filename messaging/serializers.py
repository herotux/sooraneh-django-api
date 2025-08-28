from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Friendship, Message
from users.serializers import SimpleUserSerializer

User = get_user_model()


class FriendshipSerializer(serializers.ModelSerializer):
    """
    Serializer for the Friendship model.
    """
    from_user = SimpleUserSerializer(read_only=True)
    to_user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at']
        read_only_fields = ['from_user', 'status', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    """
    sender = SimpleUserSerializer(read_only=True)
    recipient = SimpleUserSerializer(read_only=True)
    recipient_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='recipient', write_only=True
    )

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'recipient',
            'recipient_id',
            'content',
            'timestamp',
            'is_read'
        ]
        read_only_fields = ['sender', 'timestamp', 'is_read']

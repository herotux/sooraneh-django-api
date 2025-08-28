from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Friendship, Message
from finances.models import Person
from .serializers import FriendshipSerializer, SimpleUserSerializer, MessageSerializer

User = get_user_model()


class MessageViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and sending messages.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This queryset returns all messages where the user is either the sender or the recipient.
        """
        user = self.request.user
        return Message.objects.filter(Q(sender=user) | Q(recipient=user))

    def perform_create(self, serializer):
        """
        Set the sender to the current user.
        """
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=['get'])
    def inbox(self, request):
        """
        Returns a list of users that the current user has had a conversation with.
        """
        user = request.user
        # Get IDs of users the current user has sent messages to or received messages from
        sent_to_ids = Message.objects.filter(sender=user).values_list('recipient_id', flat=True)
        received_from_ids = Message.objects.filter(recipient=user).values_list('sender_id', flat=True)

        # Combine and get unique user IDs
        user_ids = set(list(sent_to_ids) + list(received_from_ids))

        # Get user objects
        conversations = User.objects.filter(id__in=user_ids)
        serializer = SimpleUserSerializer(conversations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        """
        Returns the message history with a specific user.
        """
        user = request.user
        try:
            other_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        messages = Message.objects.filter(
            (Q(sender=user, recipient=other_user) | Q(sender=other_user, recipient=user))
        ).order_by('timestamp')

        # Mark messages as read
        messages.filter(recipient=user, is_read=False).update(is_read=True)

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class FriendshipViewSet(viewsets.ViewSet):
    """
    A ViewSet for managing friendships.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        List all accepted friends.
        """
        accepted_friendships = Friendship.objects.filter(
            (Q(from_user=request.user) | Q(to_user=request.user)),
            status='ACCEPTED'
        )
        friends = []
        for friendship in accepted_friendships:
            if friendship.from_user == request.user:
                friends.append(friendship.to_user)
            else:
                friends.append(friendship.from_user)

        serializer = SimpleUserSerializer(friends, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        List all pending friend requests received by the user.
        """
        pending_requests = Friendship.objects.filter(to_user=request.user, status='PENDING')
        serializer = FriendshipSerializer(pending_requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='send-request')
    def send_request(self, request):
        """
        Send a friend request to a user.
        Expects {"user_id": <id>} in the request body.
        """
        to_user_id = request.data.get('user_id')
        if not to_user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            to_user = User.objects.get(pk=to_user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user == to_user:
            return Response({"error": "You cannot send a friend request to yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a request already exists
        if Friendship.objects.filter(
            (Q(from_user=request.user, to_user=to_user) | Q(from_user=to_user, to_user=request.user))
        ).exists():
            return Response({"error": "A friend request already exists between you and this user."}, status=status.HTTP_400_BAD_REQUEST)

        friendship = Friendship.objects.create(from_user=request.user, to_user=to_user)
        serializer = FriendshipSerializer(friendship)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """
        Accept a friend request with the given pk.
        This also creates corresponding Person objects for both users.
        """
        try:
            friend_request = Friendship.objects.get(pk=pk, to_user=request.user, status='PENDING')
        except Friendship.DoesNotExist:
            return Response({"error": "Friend request not found or you are not the recipient."}, status=status.HTTP_404_NOT_FOUND)

        friend_request.status = 'ACCEPTED'
        friend_request.save()

        # Create Person objects for each user in the other's contacts
        from_user = friend_request.from_user
        to_user = friend_request.to_user

        # Create a Person for from_user in to_user's contacts
        Person.objects.get_or_create(
            user=to_user,
            linked_user=from_user,
            defaults={'first_name': from_user.first_name, 'last_name': from_user.last_name, 'relation': 'Friend'}
        )
        # Create a Person for to_user in from_user's contacts
        Person.objects.get_or_create(
            user=from_user,
            linked_user=to_user,
            defaults={'first_name': to_user.first_name, 'last_name': to_user.last_name, 'relation': 'Friend'}
        )

        serializer = FriendshipSerializer(friend_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def unfriend(self, request, pk=None):
        """
        Remove a friend connection. The pk is the user ID of the friend.
        """
        try:
            friend_to_remove = User.objects.get(pk=pk)
            friendship = Friendship.objects.get(
                (Q(from_user=request.user, to_user=friend_to_remove) |
                 Q(from_user=friend_to_remove, to_user=request.user)),
                status='ACCEPTED'
            )
            friendship.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (User.DoesNotExist, Friendship.DoesNotExist):
            return Response({"error": "Friendship not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a friend request with the given pk.
        """
        try:
            friend_request = Friendship.objects.get(pk=pk, to_user=request.user, status='PENDING')
        except Friendship.DoesNotExist:
            return Response({"error": "Friend request not found or you are not the recipient."}, status=status.HTTP_404_NOT_FOUND)

        friend_request.delete() # Or set status to REJECTED, deleting is cleaner for this implementation
        return Response(status=status.HTTP_204_NO_CONTENT)

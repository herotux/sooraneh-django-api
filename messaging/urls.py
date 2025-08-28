from rest_framework.routers import DefaultRouter
from .views import FriendshipViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'friends', FriendshipViewSet, basename='friendship')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = router.urls

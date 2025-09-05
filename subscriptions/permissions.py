from rest_framework.permissions import BasePermission
from django.utils import timezone

class HasFeaturePermission(BasePermission):
    """
    Custom permission to check if a user's plan allows a specific feature.
    Usage: permission_classes = [HasFeaturePermission.for_feature('feature_flag_name')]
    """
    feature_flag = None

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            subscription = request.user.subscription
            if not subscription.is_active or subscription.end_date < timezone.now():
                return False # Subscription is inactive or expired

            # Check the feature flag on the user's plan
            return getattr(subscription.plan, self.feature_flag, False)
        except AttributeError:
            # This handles cases where user has no subscription object
            return False

    @classmethod
    def for_feature(cls, feature_flag):
        """
        A factory method to create a permission class for a specific feature flag.
        """
        return type(
            f"Has{feature_flag.title().replace('_','')}Permission",
            (cls,),
            {'feature_flag': feature_flag}
        )

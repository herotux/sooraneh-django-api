from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum
from .models import Building, Unit, BuildingExpense, MaintenanceFee
from .serializers import (
    BuildingSerializer,
    UnitSerializer,
    BuildingExpenseSerializer,
    MaintenanceFeeSerializer
)
from subscriptions.permissions import HasFeaturePermission
from django.shortcuts import get_object_or_404
from django.utils import timezone


class BuildingViewSet(viewsets.ModelViewSet):
    """
    یک ViewSet برای مدیریت ساختمان‌ها.

    - **list**: ساختمان‌هایی را که شما مدیر آن هستید یا در آن ساکن هستید، نمایش می‌دهد.
    - **create**: یک ساختمان جدید ایجاد می‌کند و شما را به عنوان مدیر آن قرار می‌دهد.
    - **retrieve/update/destroy**: جزئیات یک ساختمان را مدیریت می‌کند (فقط برای مدیر).
    """
    serializer_class = BuildingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        کاربران ساختمان‌هایی را می‌بینند که یا مدیر آن هستند یا در یکی از واحدهای آن ساکن هستند.
        """
        user = self.request.user
        return Building.objects.filter(
            Q(manager=user) | Q(units__resident=user)
        ).distinct()

    def perform_create(self, serializer):
        """
        هنگام ایجاد ساختمان، کاربر فعلی به عنوان مدیر ثبت می‌شود.
        """
        serializer.save(manager=self.request.user)

    def get_permissions(self):
        """
        - Only the manager can edit or delete.
        - Only users with the 'can_manage_buildings' plan can create.
        """
        if self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated, HasFeaturePermission.for_feature('can_manage_buildings')]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsManagerPermission]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        ارائه خلاصه وضعیت مالی ساختمان.

        این ویو مجموع هزینه‌های ثبت شده و مجموع شارژهای پرداخت شده را محاسبه کرده و موجودی نهایی را نمایش می‌دهد.
        این گزارش برای مدیر و تمام ساکنین ساختمان قابل مشاهده است.
        """
        building = self.get_object() # The get_queryset already ensures user has access

        # Calculate total expenses
        total_expenses = building.expenses.aggregate(total=Sum('amount'))['total'] or 0

        # Calculate total paid fees
        total_income = MaintenanceFee.objects.filter(
            unit__building=building,
            is_paid=True
        ).aggregate(total=Sum('amount'))['total'] or 0

        balance = total_income - total_expenses

        return Response({
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': balance
        })


class UnitViewSet(viewsets.ModelViewSet):
    """
    یک ViewSet برای مدیریت واحدها در یک ساختمان خاص.

    این ViewSet به صورت تو در تو در `BuildingViewSet` استفاده می‌شود.
    - **list/retrieve**: نمایش واحدها برای تمام ساکنین و مدیر.
    - **create/update/destroy**: مدیریت واحدها (فقط برای مدیر ساختمان).
    """
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        واحدها را بر اساس ساختمان مشخص شده در URL فیلتر می‌کند.
        """
        building_pk = self.kwargs.get('building_pk')
        building = get_object_or_404(Building, pk=building_pk)
        return Unit.objects.filter(building=building)

    def perform_create(self, serializer):
        """
        واحد جدید را به ساختمان مشخص شده در URL مرتبط می‌کند.
        """
        building_pk = self.kwargs.get('building_pk')
        building = get_object_or_404(Building, pk=building_pk)
        serializer.save(building=building)

    def get_permissions(self):
        """
        فقط مدیر ساختمان می‌تواند واحدها را مدیریت (ایجاد، ویرایش، حذف) کند.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsManagerOfBuildingPermission]
        return super().get_permissions()


# --- Custom Permissions ---

class IsManagerPermission(permissions.BasePermission):
    """
    اجازه دسترسی فقط به مدیر ساختمان.
    """
    def has_object_permission(self, request, view, obj):
        return obj.manager == request.user

class IsManagerOfBuildingPermission(permissions.BasePermission):
    """
    اجازه دسترسی فقط به مدیر ساختمانی که از URL گرفته شده.
    """
    def has_permission(self, request, view):
        building_pk = view.kwargs.get('building_pk')
        building = get_object_or_404(Building, pk=building_pk)
        return building.manager == request.user


class BuildingExpenseViewSet(viewsets.ModelViewSet):
    """
    API for managing building expenses. Only the building manager can create/edit/delete.
    """
    serializer_class = BuildingExpenseSerializer
    permission_classes = [IsManagerOfBuildingPermission]

    def get_queryset(self):
        building_pk = self.kwargs.get('building_pk')
        return BuildingExpense.objects.filter(building_id=building_pk)

    def perform_create(self, serializer):
        building_pk = self.kwargs.get('building_pk')
        building = get_object_or_404(Building, pk=building_pk)
        serializer.save(building=building)


class MaintenanceFeeViewSet(viewsets.ModelViewSet):
    """
    API for managing monthly maintenance fees (sharj).
    - Manager can create/edit/delete fees for any unit.
    - Resident can only view their own fees and mark them as paid.
    """
    serializer_class = MaintenanceFeeSerializer

    def get_queryset(self):
        unit_pk = self.kwargs.get('unit_pk')
        return MaintenanceFee.objects.filter(unit_id=unit_pk)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManagerOfBuildingViaUnitPermission()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        unit_pk = self.kwargs.get('unit_pk')
        unit = get_object_or_404(Unit, pk=unit_pk)
        serializer.save(unit=unit)

    @action(detail=True, methods=['post'])
    def pay(self, request, building_pk=None, unit_pk=None, pk=None):
        """
        Marks a maintenance fee as paid. Can only be done by the resident of the unit.
        """
        fee = self.get_object()
        if fee.unit.resident != request.user:
            return Response({'error': 'You can only pay fees for your own unit.'}, status=status.HTTP_403_FORBIDDEN)

        fee.is_paid = True
        fee.payment_date = timezone.now().date()
        fee.save()
        serializer = self.get_serializer(fee)
        return Response(serializer.data)


class IsManagerOfBuildingViaUnitPermission(permissions.BasePermission):
    """
    Permission to check if the user is the manager of the building
    that the unit belongs to.
    """
    def has_permission(self, request, view):
        unit_pk = view.kwargs.get('unit_pk')
        unit = get_object_or_404(Unit, pk=unit_pk)
        return unit.building.manager == request.user

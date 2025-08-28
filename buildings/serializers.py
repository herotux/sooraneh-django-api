from rest_framework import serializers
from .models import Building, Unit, BuildingExpense, MaintenanceFee
from users.serializers import SimpleUserSerializer


class UnitSerializer(serializers.ModelSerializer):
    """
    Serializer for a single Unit within a building.
    Includes resident information.
    """
    resident = SimpleUserSerializer(read_only=True)
    resident_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True, source='resident'
    )

    class Meta:
        model = Unit
        fields = ['id', 'unit_number', 'resident', 'resident_id']


class BuildingSerializer(serializers.ModelSerializer):
    """
    Serializer for a Building.
    Includes basic information and the manager's details.
    For viewing units, use the dedicated nested endpoint.
    """
    manager = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Building
        fields = ['id', 'name', 'address', 'manager']
        read_only_fields = ['manager']


class BuildingExpenseSerializer(serializers.ModelSerializer):
    """
    Serializer for building expenses.
    """
    class Meta:
        model = BuildingExpense
        fields = ['id', 'description', 'amount', 'date']


class MaintenanceFeeSerializer(serializers.ModelSerializer):
    """
    Serializer for maintenance fees (sharj).
    """
    unit = UnitSerializer(read_only=True)

    class Meta:
        model = MaintenanceFee
        fields = ['id', 'unit', 'amount', 'due_date', 'is_paid', 'payment_date']
        read_only_fields = ['is_paid', 'payment_date']

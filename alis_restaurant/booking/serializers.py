from rest_framework import serializers
from .models import Table, Booking

class TableSerializer(serializers.ModelSerializer):
    """Serializer for Table model"""
    class Meta:
        model = Table
        fields = ['id', 'table_number', 'capacity', 'is_active']

class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model"""
    user = serializers.ReadOnlyField(source='user.username')
    table = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'table', 'booking_date', 'booking_time', 
            'number_of_guests', 'status', 'special_requests', 
            'contact_phone', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """Validate booking data"""
        # Validation is handled in the model's clean method
        # Additional API-specific validation can be added here
        return data

class AvailableTablesSerializer(serializers.Serializer):
    """Serializer for checking available tables"""
    date = serializers.DateField(required=True)
    time = serializers.TimeField(required=True)
    party_size = serializers.IntegerField(required=True, min_value=1, max_value=20)


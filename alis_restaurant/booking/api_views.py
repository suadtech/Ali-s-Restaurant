from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
import datetime

from .models import Table, Booking
from .serializers import TableSerializer, BookingSerializer, AvailableTablesSerializer
from .views import find_available_tables

class TableViewSet(viewsets.ModelViewSet):
    """API endpoint for tables"""
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [permissions.IsAuthenticated]

class BookingViewSet(viewsets.ModelViewSet):
    """API endpoint for bookings"""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return bookings for the current user only"""
        return Booking.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user and find an available table"""
        booking_date = serializer.validated_data.get('booking_date')
        booking_time = serializer.validated_data.get('booking_time')
        number_of_guests = serializer.validated_data.get('number_of_guests')
        
        # Find an available table
        available_tables = find_available_tables(booking_date, booking_time, number_of_guests)
        
        if not available_tables:
            return Response(
                {"error": "No tables available for the selected date and time."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Assign the first available table
        serializer.save(user=self.request.user, table=available_tables[0])

class AvailableTablesAPIView(APIView):
    """API endpoint to check for available tables"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Check for available tables based on date, time, and party size"""
        serializer = AvailableTablesSerializer(data=request.data)
        
        if serializer.is_valid():
            date = serializer.validated_data.get('date')
            time = serializer.validated_data.get('time')
            party_size = serializer.validated_data.get('party_size')
            
            # Check if date is in the past
            if date < timezone.now().date():
                return Response(
                    {"error": "Booking date cannot be in the past"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if restaurant is open at the requested time
            # Assuming restaurant hours are 11:00 AM to 10:00 PM
            opening_time = datetime.time(11, 0)
            closing_time = datetime.time(22, 0)
            
            if time < opening_time or time > closing_time:
                return Response(
                    {"error": "The restaurant is only open from 11:00 AM to 10:00 PM."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Find available tables
            available_tables = find_available_tables(date, time, party_size)
            
            # Serialize the available tables
            table_serializer = TableSerializer(available_tables, many=True)
            
            return Response({
                "date": date,
                "time": time,
                "party_size": party_size,
                "available_tables": table_serializer.data,
                "has_availability": len(available_tables) > 0
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


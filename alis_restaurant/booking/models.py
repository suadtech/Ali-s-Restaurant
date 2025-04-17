from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime

# Create your models here.
class Table(models.Model):
    """Model representing a restaurant table"""
    table_number = models.IntegerField(unique=True)
    capacity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Table {self.table_number} (Capacity: {self.capacity})"
    
    class Meta:
        ordering = ['table_number']

class Booking(models.Model):
    """Model representing a booking"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    booking_time = models.TimeField()
    number_of_guests = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    special_requests = models.TextField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20)
    
    def __str__(self):
        return f"Booking for {self.user.username} - {self.booking_date} at {self.booking_time}"
    
    def clean(self):
        """Validate booking to prevent double bookings and past dates"""
        # Check if booking date is in the past
        if self.booking_date < timezone.now().date():
            raise ValidationError("Booking date cannot be in the past")
        
        # Check if booking time is at least 1 hour from now for same-day bookings
        if self.booking_date == timezone.now().date():
            booking_datetime = datetime.datetime.combine(
                self.booking_date, 
                self.booking_time, 
                tzinfo=timezone.get_current_timezone()
            )
            if booking_datetime < timezone.now() + datetime.timedelta(hours=1):
                raise ValidationError("Booking must be at least 1 hour from now")
        
        # Check for double bookings
        # A table is considered double-booked if there's an overlap of 2 hours
        booking_start = datetime.datetime.combine(
            self.booking_date, 
            self.booking_time, 
            tzinfo=timezone.get_current_timezone()
        )
        booking_end = booking_start + datetime.timedelta(hours=2)
        
        overlapping_bookings = Booking.objects.filter(
            table=self.table,
            booking_date=self.booking_date,
            status__in=['pending', 'confirmed'],
        ).exclude(id=self.id)
        
        for booking in overlapping_bookings:
            existing_start = datetime.datetime.combine(
                booking.booking_date, 
                booking.booking_time, 
                tzinfo=timezone.get_current_timezone()
            )
            existing_end = existing_start + datetime.timedelta(hours=2)
            
            if (booking_start <= existing_end and booking_end >= existing_start):
                raise ValidationError(f"This table is already booked during this time slot")
        
        # Check if table capacity is sufficient
        if self.table.capacity < self.number_of_guests:
            raise ValidationError(f"Table capacity ({self.table.capacity}) is less than the number of guests ({self.number_of_guests})")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-booking_date', '-booking_time']
        indexes = [
            models.Index(fields=['booking_date', 'booking_time']),
            models.Index(fields=['status']),
        ]


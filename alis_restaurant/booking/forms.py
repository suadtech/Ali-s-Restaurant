from django import forms
from .models import Booking
from django.utils import timezone
import datetime

class BookingForm(forms.ModelForm):
    """Form for creating and updating bookings"""
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date().isoformat()}),
        help_text="Select a date for your booking"
    )
    booking_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        help_text="Select a time for your booking"
    )
    
    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'number_of_guests', 'special_requests', 'contact_phone']
        widgets = {
            'special_requests': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('booking_date')
        booking_time = cleaned_data.get('booking_time')
        
        # Additional validation beyond model validation
        if booking_date and booking_time:
            # Check if restaurant is open at the requested time
            # Assuming restaurant hours are 11:00 AM to 10:00 PM
            opening_time = datetime.time(11, 0)
            closing_time = datetime.time(22, 0)
            
            if booking_time < opening_time or booking_time > closing_time:
                raise forms.ValidationError(
                    "The restaurant is only open from 11:00 AM to 10:00 PM."
                )
            
            # Check if booking is at least 1 hour from now for same-day bookings
            if booking_date == timezone.now().date():
                booking_datetime = datetime.datetime.combine(
                    booking_date, 
                    booking_time, 
                    tzinfo=timezone.get_current_timezone()
                )
                if booking_datetime < timezone.now() + datetime.timedelta(hours=1):
                    raise forms.ValidationError(
                        "Booking must be at least 1 hour from now for same-day reservations."
                    )
        
        return cleaned_data

class AvailableTablesForm(forms.Form):
    """Form for checking available tables"""
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date().isoformat()}),
        help_text="Select a date to check availability"
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        help_text="Select a time to check availability"
    )
    party_size = forms.IntegerField(
        min_value=1,
        max_value=20,
        help_text="Enter the number of guests"
    )


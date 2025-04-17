from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
import datetime

from .models import Table, Booking
from .forms import BookingForm, AvailableTablesForm


# Create your views here.
def booking_home(request):
    """Home page for the booking system"""
    form = AvailableTablesForm()
    context = {
        'form': form,
    }
    return render(request, 'booking/booking_home.html', context)

@login_required
def create_booking(request):
    """Create a new booking"""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            
            # Find an available table for the booking
            available_tables = find_available_tables(
                booking.booking_date,
                booking.booking_time,
                booking.number_of_guests
            )
            
            if not available_tables:
                messages.error(request, "Sorry, no tables are available for the selected date and time.")
                return render(request, 'booking/create_booking.html', {'form': form})
            
            # Assign the first available table
            booking.table = available_tables[0]
            
            try:
                booking.save()
                messages.success(request, "Your booking has been created successfully!")
                return redirect('booking:booking_detail', booking_id=booking.id)
            except Exception as e:
                messages.error(request, f"Error creating booking: {str(e)}")
    else:
        form = BookingForm()
    
    context = {
        'form': form,
    }
    return render(request, 'booking/create_booking.html', context)

@login_required
def booking_list(request):
    """List all bookings for the current user"""
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date', '-booking_time')
    context = {
        'bookings': bookings,
    }
    return render(request, 'booking/booking_list.html', context)

@login_required
def booking_detail(request, booking_id):
    """View details of a specific booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    context = {
        'booking': booking,
    }
    return render(request, 'booking/booking_detail.html', context)

@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Only allow cancellation if booking is not in the past and not already cancelled
    if booking.booking_date < timezone.now().date():
        messages.error(request, "Cannot cancel a booking that has already passed.")
        return redirect('booking:booking_detail', booking_id=booking.id)
    
    if booking.status == 'cancelled':
        messages.error(request, "This booking has already been cancelled.")
        return redirect('booking:booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Your booking has been cancelled successfully.")
        return redirect('booking:booking_list')
    
    context = {
        'booking': booking,
    }
    return render(request, 'booking/cancel_booking.html', context)

def available_tables(request):
    """Check for available tables"""
    if request.method == 'POST':
        form = AvailableTablesForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            party_size = form.cleaned_data['party_size']
            
            available = find_available_tables(date, time, party_size)
            
            context = {
                'form': form,
                'available_tables': available,
                'date': date,
                'time': time,
                'party_size': party_size,
                'has_availability': len(available) > 0,
            }
            return render(request, 'booking/available_tables.html', context)
    else:
        form = AvailableTablesForm()
    
    context = {
        'form': form,
    }
    return render(request, 'booking/available_tables.html', context)

def find_available_tables(date, time, party_size):
    """Helper function to find available tables for a given date, time, and party size"""
    # Get all active tables that can accommodate the party size
    suitable_tables = Table.objects.filter(is_active=True, capacity__gte=party_size)
    
    # Calculate booking start and end times (assuming 2-hour booking duration)
    booking_start = datetime.datetime.combine(
        date, 
        time, 
        tzinfo=timezone.get_current_timezone()
    )
    booking_end = booking_start + datetime.timedelta(hours=2)
    
    # Find tables that are already booked during this time
    booked_table_ids = Booking.objects.filter(
        booking_date=date,
        status__in=['pending', 'confirmed'],
    ).exclude(
        # Exclude bookings that end before our start or start after our end
        Q(booking_time__lt=(booking_start - datetime.timedelta(hours=2)).time()) | 
        Q(booking_time__gt=booking_end.time())
    ).values_list('table_id', flat=True)
    
    # Filter out booked tables
    available_tables = suitable_tables.exclude(id__in=booked_table_ids)
    
    return list(available_tables)

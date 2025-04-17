from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from booking.models import Table, Booking


# Create your tests here.
class TableModelTest(TestCase):
    """Test cases for the Table model"""
    
    def setUp(self):
        """Set up test data"""
        Table.objects.create(table_number=1, capacity=4, is_active=True)
        Table.objects.create(table_number=2, capacity=2, is_active=True)
        Table.objects.create(table_number=3, capacity=6, is_active=False)
    
    def test_table_creation(self):
        """Test that tables are created correctly"""
        table1 = Table.objects.get(table_number=1)
        table2 = Table.objects.get(table_number=2)
        table3 = Table.objects.get(table_number=3)
        
        self.assertEqual(table1.capacity, 4)
        self.assertTrue(table1.is_active)
        
        self.assertEqual(table2.capacity, 2)
        self.assertTrue(table2.is_active)
        
        self.assertEqual(table3.capacity, 6)
        self.assertFalse(table3.is_active)
    
    def test_table_string_representation(self):
        """Test the string representation of Table objects"""
        table = Table.objects.get(table_number=1)
        self.assertEqual(str(table), "Table 1 (Capacity: 4)")

class BookingModelTest(TestCase):
    """Test cases for the Booking model"""
    
    def setUp(self):
        """Set up test data"""
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create tables
        self.table1 = Table.objects.create(table_number=1, capacity=4, is_active=True)
        self.table2 = Table.objects.create(table_number=2, capacity=2, is_active=True)
        
        # Create a booking for tomorrow
        tomorrow = timezone.now().date() + timedelta(days=1)
        self.booking1 = Booking.objects.create(
            user=self.user,
            table=self.table1,
            booking_date=tomorrow,
            booking_time=timezone.now().time(),
            number_of_guests=3,
            status='confirmed',
            contact_phone='555-1234'
        )
    
    def test_booking_creation(self):
        """Test that bookings are created correctly"""
        booking = Booking.objects.get(id=self.booking1.id)
        
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.table, self.table1)
        self.assertEqual(booking.number_of_guests, 3)
        self.assertEqual(booking.status, 'confirmed')
        self.assertEqual(booking.contact_phone, '555-1234')
    
    def test_booking_string_representation(self):
        """Test the string representation of Booking objects"""
        booking = Booking.objects.get(id=self.booking1.id)
        expected = f"Booking for {self.user.username} - {booking.booking_date} at {booking.booking_time}"
        self.assertEqual(str(booking), expected)
    
    def test_booking_validation_past_date(self):
        """Test that bookings cannot be made for past dates"""
        yesterday = timezone.now().date() - timedelta(days=1)
        
        with self.assertRaises(Exception):
            Booking.objects.create(
                user=self.user,
                table=self.table2,
                booking_date=yesterday,
                booking_time=timezone.now().time(),
                number_of_guests=2,
                status='pending',
                contact_phone='555-5678'
            )
    
    def test_booking_validation_table_capacity(self):
        """Test that bookings cannot exceed table capacity"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        with self.assertRaises(Exception):
            Booking.objects.create(
                user=self.user,
                table=self.table2,  # capacity is 2
                booking_date=tomorrow,
                booking_time=timezone.now().time(),
                number_of_guests=3,  # exceeds capacity
                status='pending',
                contact_phone='555-5678'
            )


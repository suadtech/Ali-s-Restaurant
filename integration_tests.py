from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from booking.models import Table, Booking
from menu.models import Category, MenuItem

class IntegrationTest(TestCase):
    """Integration tests for the entire application flow"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create a test user
        self.user = User.objects.create_user(
            username='integrationuser',
            email='integration@example.com',
            password='testpassword123'
        )
        
        # Create tables
        self.table = Table.objects.create(table_number=10, capacity=4, is_active=True)
        
        # Create menu categories and items
        self.category = Category.objects.create(name="Test Category", is_active=True)
        self.menu_item = MenuItem.objects.create(
            name="Test Item",
            description="Test description",
            price=9.99,
            category=self.category,
            is_available=True
        )
    
    def test_full_booking_flow(self):
        """Test the complete booking flow from login to booking creation"""
        # Step 1: Login
        login_response = self.client.post(reverse('login'), {
            'username': 'integrationuser',
            'password': 'testpassword123'
        })
        self.assertEqual(login_response.status_code, 302)  # Redirect after login
        
        # Step 2: Visit booking home page
        booking_home_response = self.client.get(reverse('booking:booking_home'))
        self.assertEqual(booking_home_response.status_code, 200)
        
        # Step 3: Create a booking
        tomorrow = timezone.now().date() + timedelta(days=1)
        booking_time = timezone.now().replace(hour=18, minute=0, second=0).time()
        
        create_booking_response = self.client.post(reverse('booking:create_booking'), {
            'booking_date': tomorrow,
            'booking_time': booking_time,
            'number_of_guests': 2,
            'special_requests': 'Test request',
            'contact_phone': '555-1234'
        })
        
        # Should redirect to booking detail page after successful creation
        self.assertEqual(create_booking_response.status_code, 302)
        
        # Step 4: Verify booking was created
        bookings = Booking.objects.filter(user=self.user)
        self.assertEqual(bookings.count(), 1)
        
        # Step 5: Check booking list page
        booking_list_response = self.client.get(reverse('booking:booking_list'))
        self.assertEqual(booking_list_response.status_code, 200)
        self.assertContains(booking_list_response, '555-1234')
        
        # Step 6: Check booking detail page
        booking = bookings.first()
        booking_detail_response = self.client.get(
            reverse('booking:booking_detail', kwargs={'booking_id': booking.id})
        )
        self.assertEqual(booking_detail_response.status_code, 200)
        self.assertContains(booking_detail_response, 'Test request')
    
    def test_menu_browsing_flow(self):
        """Test the menu browsing flow"""
        # Step 1: Visit menu home page
        menu_home_response = self.client.get(reverse('menu:menu_home'))
        self.assertEqual(menu_home_response.status_code, 200)
        
        # Step 2: View category detail
        category_detail_response = self.client.get(
            reverse('menu:category_detail', kwargs={'category_id': self.category.id})
        )
        self.assertEqual(category_detail_response.status_code, 200)
        self.assertContains(category_detail_response, 'Test Item')
        
        # Step 3: View menu item detail
        item_detail_response = self.client.get(
            reverse('menu:menu_item_detail', kwargs={'item_id': self.menu_item.id})
        )
        self.assertEqual(item_detail_response.status_code, 200)
        self.assertContains(item_detail_response, 'Test description')
        self.assertContains(item_detail_response, '9.99')
    
    def test_user_profile_flow(self):
        """Test the user profile flow"""
        # Step 1: Login
        self.client.login(username='integrationuser', password='testpassword123')
        
        # Step 2: Visit profile page
        profile_response = self.client.get(reverse('profile'))
        self.assertEqual(profile_response.status_code, 200)
        self.assertContains(profile_response, 'integrationuser')
        
        # Step 3: Update profile
        update_profile_response = self.client.post(reverse('profile'), {
            'username': 'integrationuser',
            'email': 'updated@example.com',
            'first_name': 'Integration',
            'last_name': 'User'
        })
        self.assertEqual(update_profile_response.status_code, 302)  # Redirect after update
        
        # Step 4: Verify profile was updated
        user = User.objects.get(username='integrationuser')
        self.assertEqual(user.email, 'updated@example.com')
        self.assertEqual(user.first_name, 'Integration')
        self.assertEqual(user.last_name, 'User')


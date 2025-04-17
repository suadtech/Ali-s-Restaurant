from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
class UserAuthenticationTest(TestCase):
    """Test cases for user authentication functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
        
        # Create a test user
        self.test_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpassword123'
        )
    
    def test_user_registration(self):
        """Test user registration functionality"""
        # Test registration with valid data
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'complex_password123',
            'password2': 'complex_password123'
        })
        
        # Check redirect to login page after successful registration
        self.assertRedirects(response, self.login_url)
        
        # Verify user was created in the database
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Test registration with existing username
        response = self.client.post(self.register_url, {
            'username': 'existinguser',
            'email': 'another@example.com',
            'password1': 'complex_password123',
            'password2': 'complex_password123'
        })
        
        # Should stay on registration page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with that username already exists')
    
    def test_user_login(self):
        """Test user login functionality"""
        # Test login with valid credentials
        response = self.client.post(self.login_url, {
            'username': 'existinguser',
            'password': 'testpassword123'
        })
        
        # Check if user is logged in and redirected to home page
        self.assertEqual(response.status_code, 302)  # Redirect status code
        
        # Test login with invalid credentials
        response = self.client.post(self.login_url, {
            'username': 'existinguser',
            'password': 'wrongpassword'
        })
        
        # Should stay on login page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')
    
    def test_profile_access(self):
        """Test profile page access restrictions"""
        # Try accessing profile without login
        response = self.client.get(self.profile_url)
        
        # Should redirect to login page
        self.assertRedirects(response, f'/accounts/login/?next={self.profile_url}')
        
        # Login and try again
        self.client.login(username='existinguser', password='testpassword123')
        response = self.client.get(self.profile_url)
        
        # Should access profile page successfully
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'existinguser')

class BookingViewsTest(TestCase):
    """Test cases for booking views functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create a test user
        self.user = User.objects.create_user(
            username='bookinguser',
            email='booking@example.com',
            password='testpassword123'
        )
        
        # Login the user
        self.client.login(username='bookinguser', password='testpassword123')
        
        # URLs
        self.booking_home_url = reverse('booking:booking_home')
        self.create_booking_url = reverse('booking:create_booking')
        self.booking_list_url = reverse('booking:booking_list')
    
    def test_booking_home_access(self):
        """Test access to booking home page"""
        response = self.client.get(self.booking_home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Book a Table')
    
    def test_booking_list_access(self):
        """Test access to booking list page"""
        response = self.client.get(self.booking_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Bookings')
    
    def test_create_booking_access(self):
        """Test access to create booking page"""
        response = self.client.get(self.create_booking_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Make a Reservation')

class MenuViewsTest(TestCase):
    """Test cases for menu views functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # URLs
        self.menu_home_url = reverse('menu:menu_home')
    
    def test_menu_home_access(self):
        """Test access to menu home page"""
        response = self.client.get(self.menu_home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Our Menu')


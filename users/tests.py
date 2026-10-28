from django.test import TestCase, Client
from django.contrib.auth import get_user_model, authenticate
from django.urls import reverse
from django.core.management import call_command
from users.models import CustomerProfile, DeliveryAgentProfile

User = get_user_model()


class UserAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            username='rifat_customer',
            email='rifat@gmail.com',
            password='123456',
            phone_number='+8801711000001',
            user_type='customer'
        )
        self.admin = User.objects.create_superuser(
            username='rifat_admin',
            email='rifatadmin@gmail.com',
            password='123456',
            phone_number='+8801711000002',
            user_type='admin'
        )

    def test_customer_email_authentication(self):
        """Test authenticating customer with email."""
        user = authenticate(username='rifat@gmail.com', password='123456')
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'rifat@gmail.com')
        self.assertEqual(user.user_type, 'customer')
        self.assertFalse(user.is_staff)

    def test_admin_email_authentication(self):
        """Test authenticating admin with email and staff privileges."""
        user = authenticate(username='rifatadmin@gmail.com', password='123456')
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'rifatadmin@gmail.com')
        self.assertEqual(user.user_type, 'admin')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_case_insensitive_email_login(self):
        """Test email login is case-insensitive."""
        user = authenticate(username='RIFAT@GMAIL.COM', password='123456')
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.customer.pk)

    def test_invalid_password_fails(self):
        """Test that invalid password fails authentication."""
        user = authenticate(username='rifat@gmail.com', password='wrongpassword')
        self.assertIsNone(user)

    def test_seed_demo_accounts_idempotent(self):
        """Test running seed_demo_accounts creates/updates accounts without duplicating."""
        call_command('seed_demo_accounts')
        # Run again to ensure idempotency
        call_command('seed_demo_accounts')

        customer_count = User.objects.filter(email='rifat@gmail.com').count()
        admin_count = User.objects.filter(email='rifatadmin@gmail.com').count()
        self.assertEqual(customer_count, 1)
        self.assertEqual(admin_count, 1)

    def test_customer_access_control(self):
        """Test ordinary customer cannot access admin dashboard."""
        self.client.login(username='rifat@gmail.com', password='123456')
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirects away with error message

    def test_admin_access_allowed(self):
        """Test admin can access admin dashboard."""
        self.client.login(username='rifatadmin@gmail.com', password='123456')
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertEqual(response.status_code, 200)

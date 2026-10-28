from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal

from orders.models import ProductService, Order
from payments.models import Payment
from delivery.models import DeliveryArea

User = get_user_model()


class DashboardSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            username='dash_cust',
            email='dash_cust@swiftdrop.local',
            password='password123',
            phone_number='+8801755000001',
            user_type='customer'
        )
        self.admin = User.objects.create_superuser(
            username='dash_admin',
            email='dash_admin@swiftdrop.local',
            password='password123',
            phone_number='+8801755000002',
            user_type='admin'
        )

        self.area = DeliveryArea.objects.create(
            name='Gulshan',
            delivery_fee=Decimal('60.00'),
            is_active=True
        )

        self.product = ProductService.objects.create(
            name='First Aid Antiseptic',
            category='medicine',
            price=Decimal('150.00'),
            stock_quantity=15,
            is_available=True
        )

        self.order = Order.objects.create(
            customer=self.customer,
            delivery_fee=Decimal('60.00'),
            total_amount=Decimal('210.00'),
            delivery_address='Road 11, Gulshan',
            delivery_city='Gulshan',
            status='delivered'
        )
        self.payment = Payment.objects.create(
            order=self.order,
            payment_method='bkash',
            amount=Decimal('210.00'),
            transaction_id='TRX-DASH-123',
            status='completed'
        )

    def test_landing_page_renders_swiftdrop_branding(self):
        """Test landing page renders brand name and essential categories."""
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SwiftDrop')
        self.assertContains(response, 'Your Essentials. Delivered Smarter.')

    def test_contact_form_submission(self):
        """Test sending message via contact view."""
        response = self.client.post(reverse('dashboard:contact'), {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+8801700000000',
            'subject': 'order',
            'message': 'Where is my delivery?'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank you for reaching out')

    def test_user_dashboard_metrics(self):
        """Test user dashboard displays correct customer statistics."""
        self.client.login(username='dash_cust@swiftdrop.local', password='password123')
        response = self.client.get(reverse('dashboard:user_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_orders'], 1)
        self.assertEqual(response.context['delivered_orders'], 1)
        self.assertEqual(response.context['total_spent'], Decimal('210.00'))

    def test_admin_dashboard_metrics(self):
        """Test admin dashboard aggregates platform revenue and order counts."""
        self.client.login(username='dash_admin@swiftdrop.local', password='password123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_orders'], 1)
        self.assertEqual(response.context['delivered_orders'], 1)
        self.assertEqual(response.context['total_revenue'], Decimal('210.00'))

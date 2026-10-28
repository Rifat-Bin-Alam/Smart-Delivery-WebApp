from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal

from orders.models import Order
from payments.models import Payment, PaymentMethod

User = get_user_model()


class PaymentSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer1 = User.objects.create_user(
            username='pay_cust1',
            email='pay_cust1@swiftdrop.local',
            password='password123',
            phone_number='+8801733000001',
            user_type='customer'
        )
        self.customer2 = User.objects.create_user(
            username='pay_cust2',
            email='pay_cust2@swiftdrop.local',
            password='password123',
            phone_number='+8801733000002',
            user_type='customer'
        )
        self.admin = User.objects.create_superuser(
            username='pay_admin',
            email='pay_admin@swiftdrop.local',
            password='password123',
            phone_number='+8801733000003',
            user_type='admin'
        )

        self.order1 = Order.objects.create(
            customer=self.customer1,
            delivery_fee=Decimal('50.00'),
            total_amount=Decimal('200.00'),
            delivery_address='Road 1, Dhaka',
            delivery_city='Dhaka',
            status='delivered'
        )
        self.payment1 = Payment.objects.create(
            order=self.order1,
            payment_method='bkash',
            amount=Decimal('200.00'),
            transaction_id='TRX-BKASH-001',
            status='completed'
        )

        self.order2 = Order.objects.create(
            customer=self.customer2,
            delivery_fee=Decimal('50.00'),
            total_amount=Decimal('500.00'),
            delivery_address='Road 2, Dhaka',
            delivery_city='Dhaka',
            status='pending'
        )
        self.payment2 = Payment.objects.create(
            order=self.order2,
            payment_method='cash_on_delivery',
            amount=Decimal('500.00'),
            status='pending'
        )

    def test_customer_only_sees_own_payments(self):
        """Customer payment list only includes transactions for their orders."""
        self.client.login(username='pay_cust1@swiftdrop.local', password='password123')
        response = self.client.get(reverse('payments:payment_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TRX-BKASH-001')
        self.assertNotContains(response, self.order2.order_number)

    def test_payment_detail_access_restriction(self):
        """Customer cannot view another user's payment receipt."""
        self.client.login(username='pay_cust1@swiftdrop.local', password='password123')
        # Try to view customer2's payment
        response = self.client.get(reverse('payments:payment_detail', kwargs={'pk': self.payment2.pk}))
        self.assertEqual(response.status_code, 404)

    def test_admin_payment_auditing(self):
        """Admin can access administrative payment list with collection aggregations."""
        self.client.login(username='pay_admin@swiftdrop.local', password='password123')
        response = self.client.get(reverse('payments:admin_payment_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TRX-BKASH-001')
        self.assertContains(response, self.order2.order_number)
        self.assertEqual(response.context['total_collected'], Decimal('200.00'))
        self.assertEqual(response.context['pending_amount'], Decimal('500.00'))

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
import json

from orders.models import ProductService, Order, OrderItem, OrderStatusHistory
from delivery.models import DeliveryArea
from payments.models import Payment

User = get_user_model()


class OrderSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer1@swiftdrop.local',
            password='password123',
            phone_number='+8801711111111',
            user_type='customer'
        )
        self.other_customer = User.objects.create_user(
            username='customer2',
            email='customer2@swiftdrop.local',
            password='password123',
            phone_number='+8801711111112',
            user_type='customer'
        )
        self.area = DeliveryArea.objects.create(
            name='Dhanmondi',
            delivery_fee=Decimal('50.00'),
            is_active=True
        )
        self.product1 = ProductService.objects.create(
            name='Organic Milk 1L',
            category='groceries',
            price=Decimal('100.00'),
            stock_quantity=20,
            is_available=True
        )
        self.product2 = ProductService.objects.create(
            name='Paracetamol 500mg',
            category='medicine',
            price=Decimal('25.00'),
            stock_quantity=50,
            is_available=True
        )

    def test_product_catalog_listing(self):
        """Test product list view returns active items."""
        response = self.client.get(reverse('orders:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Organic Milk 1L')
        self.assertContains(response, 'Paracetamol 500mg')

    def test_create_order_server_side_calculation(self):
        """
        Verify server recalculates subtotal, delivery fee, and grand total.
        Client cannot spoof prices or totals.
        """
        self.client.login(username='customer1@swiftdrop.local', password='password123')

        payload = {
            'cart_items': [
                {'id': self.product1.id, 'quantity': 2, 'price': 1.00},  # Spoofed price 1.00
                {'id': self.product2.id, 'quantity': 4, 'price': 0.50}   # Spoofed price 0.50
            ],
            'delivery_address': 'House 12, Road 5, Dhanmondi',
            'delivery_city': 'Dhanmondi',
            'special_instructions': 'Please ring bell',
            'payment_method': 'cash_on_delivery'
        }

        response = self.client.post(
            reverse('orders:create_order_api'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))

        order = Order.objects.get(order_number=data['order_number'])
        # Actual server calculated: 2 * 100 + 4 * 25 = 200 + 100 = 300
        # + delivery_fee 50 = 350
        self.assertEqual(order.subtotal, Decimal('300.00'))
        self.assertEqual(order.delivery_fee, Decimal('50.00'))
        self.assertEqual(order.total_amount, Decimal('350.00'))

        # Check stock deduction
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.assertEqual(self.product1.stock_quantity, 18)
        self.assertEqual(self.product2.stock_quantity, 46)

        # Check payment record creation
        payment = Payment.objects.filter(order=order).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.payment_method, 'cash_on_delivery')
        self.assertEqual(payment.status, 'pending')
        self.assertEqual(payment.amount, Decimal('350.00'))

    def test_order_isolation_ownership_check(self):
        """Test customer cannot view or cancel another customer's order."""
        order = Order.objects.create(
            customer=self.customer,
            delivery_fee=Decimal('50.00'),
            total_amount=Decimal('150.00'),
            delivery_address='House 1, Dhanmondi',
            delivery_city='Dhanmondi',
            status='pending'
        )

        # Login as customer2
        self.client.login(username='customer2@swiftdrop.local', password='password123')
        response = self.client.get(reverse('orders:order_detail', kwargs={'pk': order.pk}))
        # Should be 404 because queryset is filtered by request.user
        self.assertEqual(response.status_code, 404)

    def test_cancellation_restores_stock(self):
        """Test cancelling a pending order restores inventory stock."""
        order = Order.objects.create(
            customer=self.customer,
            delivery_fee=Decimal('50.00'),
            total_amount=Decimal('150.00'),
            delivery_address='House 1, Dhanmondi',
            delivery_city='Dhanmondi',
            status='pending'
        )
        OrderItem.objects.create(
            order=order,
            product=self.product1,
            unit_price=self.product1.price,
            total_price=self.product1.price * 5,
            quantity=5
        )
        # Deduct initial
        self.product1.stock_quantity -= 5
        self.product1.save()

        self.client.login(username='customer1@swiftdrop.local', password='password123')
        response = self.client.post(reverse('orders:order_cancel', kwargs={'pk': order.pk}), {
            'reason': 'changed_mind',
            'confirm_cancellation': True
        })
        self.assertEqual(response.status_code, 302)

        order.refresh_from_db()
        self.assertEqual(order.status, 'cancelled')

        self.product1.refresh_from_db()
        self.assertEqual(self.product1.stock_quantity, 20)

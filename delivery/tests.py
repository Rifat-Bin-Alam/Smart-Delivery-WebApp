from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal

from orders.models import ProductService, Order, OrderItem
from delivery.models import DeliveryArea, DeliveryAssignment, DeliveryStatus
from payments.models import Payment
from users.models import DeliveryAgentProfile

User = get_user_model()


class DeliverySystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            username='cust',
            email='cust@swiftdrop.local',
            password='password123',
            phone_number='+8801722000001',
            user_type='customer'
        )
        self.agent_user = User.objects.create_user(
            username='rider1',
            email='rider1@swiftdrop.local',
            password='password123',
            phone_number='+8801722000002',
            user_type='delivery_agent'
        )
        self.agent_profile = DeliveryAgentProfile.objects.create(
            user=self.agent_user,
            vehicle_type='motorcycle',
            vehicle_number='DHK-HA-1234',
            license_number='DL-987654',
            is_available=True,
            total_deliveries=0
        )

        self.order = Order.objects.create(
            customer=self.customer,
            delivery_fee=Decimal('50.00'),
            total_amount=Decimal('250.00'),
            delivery_address='House 10, Road 4, Dhanmondi',
            delivery_city='Dhanmondi',
            status='confirmed'
        )
        self.payment = Payment.objects.create(
            order=self.order,
            payment_method='cash_on_delivery',
            amount=Decimal('250.00'),
            status='pending'
        )

    def test_customer_cannot_access_delivery_portal(self):
        """Test ordinary customers are forbidden from rider portal."""
        self.client.login(username='cust@swiftdrop.local', password='password123')
        response = self.client.get(reverse('delivery:my_deliveries'))
        self.assertEqual(response.status_code, 302)  # Redirects with access restriction

    def test_rider_can_view_assigned_tasks(self):
        """Test rider sees tasks assigned to them."""
        assignment = DeliveryAssignment.objects.create(
            order=self.order,
            delivery_agent=self.agent_user
        )

        self.client.login(username='rider1@swiftdrop.local', password='password123')
        response = self.client.get(reverse('delivery:my_deliveries'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.order_number)

    def test_rider_lifecycle_progression_to_delivered(self):
        """
        Test rider progresses assignment through:
        1. Pickup (marks order dispatched)
        2. Deliver (marks order delivered, COD payment completed, increments rider stats).
        """
        assignment = DeliveryAssignment.objects.create(
            order=self.order,
            delivery_agent=self.agent_user
        )

        self.client.login(username='rider1@swiftdrop.local', password='password123')

        # 1. Pickup
        pickup_res = self.client.post(
            reverse('delivery:delivery_status_update', kwargs={'pk': assignment.pk}),
            {'action': 'pickup', 'location': 'SwiftDrop Central Hub', 'notes': 'Package picked up'}
        )
        self.assertEqual(pickup_res.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'dispatched')

        # 2. Deliver
        deliver_res = self.client.post(
            reverse('delivery:delivery_status_update', kwargs={'pk': assignment.pk}),
            {'action': 'deliver', 'location': self.order.delivery_address, 'notes': 'Handed to customer'}
        )
        self.assertEqual(deliver_res.status_code, 302)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'delivered')

        # Verify COD payment marked completed
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'completed')
        self.assertIsNotNone(self.payment.paid_at)

        # Verify agent total_deliveries incremented
        self.agent_profile.refresh_from_db()
        self.assertEqual(self.agent_profile.total_deliveries, 1)

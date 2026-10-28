from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal

from orders.models import ProductService, Order, OrderItem
from reviews.models import Review

User = get_user_model()


class ReviewSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            username='rev_cust',
            email='rev_cust@swiftdrop.local',
            password='password123',
            phone_number='+8801744000001',
            user_type='customer'
        )
        self.other_user = User.objects.create_user(
            username='rev_other',
            email='rev_other@swiftdrop.local',
            password='password123',
            phone_number='+8801744000002',
            user_type='customer'
        )
        self.admin = User.objects.create_superuser(
            username='rev_admin',
            email='rev_admin@swiftdrop.local',
            password='password123',
            phone_number='+8801744000003',
            user_type='admin'
        )

        self.product = ProductService.objects.create(
            name='Daily Bread 400g',
            price=Decimal('50.00'),
            category='groceries',
            stock_quantity=10,
            is_available=True
        )

        # Delivered order (eligible for review)
        self.delivered_order = Order.objects.create(
            customer=self.customer,
            delivery_fee=Decimal('50.00'),
            total_amount=Decimal('100.00'),
            delivery_address='Uttara, Dhaka',
            delivery_city='Dhaka',
            status='delivered'
        )
        OrderItem.objects.create(
            order=self.delivered_order,
            product=self.product,
            quantity=1,
            unit_price=Decimal('50.00'),
            total_price=Decimal('50.00')
        )

        # Pending order (ineligible for review)
        self.pending_order = Order.objects.create(
            customer=self.customer,
            delivery_fee=Decimal('50.00'),
            total_amount=Decimal('100.00'),
            delivery_address='Uttara, Dhaka',
            delivery_city='Dhaka',
            status='pending'
        )

    def test_customer_can_review_delivered_order(self):
        """Verified customer can submit review for delivered order."""
        self.client.login(username='rev_cust@swiftdrop.local', password='password123')
        url = reverse('reviews:review_create', kwargs={
            'order_pk': self.delivered_order.pk,
            'product_pk': self.product.pk
        })
        response = self.client.post(url, {
            'rating': 5,
            'title': 'Fresh and prompt delivery',
            'comment': 'The bread was freshly baked and arrived in under 30 minutes!'
        })
        self.assertEqual(response.status_code, 302)

        review = Review.objects.filter(customer=self.customer, product=self.product).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 5)
        self.assertTrue(review.is_verified)
        self.assertTrue(review.is_public)

    def test_customer_cannot_review_pending_order(self):
        """Customer cannot review order that has not been delivered yet."""
        self.client.login(username='rev_cust@swiftdrop.local', password='password123')
        url = reverse('reviews:review_create', kwargs={
            'order_pk': self.pending_order.pk,
            'product_pk': self.product.pk
        })
        response = self.client.get(url)
        # Should redirect back because order is not delivered
        self.assertEqual(response.status_code, 302)

    def test_customer_cannot_review_other_users_order(self):
        """Customer cannot review another person's order."""
        self.client.login(username='rev_other@swiftdrop.local', password='password123')
        url = reverse('reviews:review_create', kwargs={
            'order_pk': self.delivered_order.pk,
            'product_pk': self.product.pk
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_admin_review_moderation(self):
        """Admin can toggle review visibility."""
        review = Review.objects.create(
            customer=self.customer,
            order=self.delivered_order,
            product=self.product,
            rating=4,
            title='Good service',
            comment='Good item',
            is_public=True
        )

        self.client.login(username='rev_admin@swiftdrop.local', password='password123')
        response = self.client.post(reverse('reviews:admin_review_list'), {
            'review_id': review.id,
            'action': 'toggle_visibility'
        })
        self.assertEqual(response.status_code, 302)

        review.refresh_from_db()
        self.assertFalse(review.is_public)

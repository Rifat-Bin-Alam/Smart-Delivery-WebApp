from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from decimal import Decimal

from orders.models import Order, ProductService
from payments.models import Payment
from delivery.models import DeliveryAssignment, DeliveryArea
from reviews.models import Review
from .models import Notification, FAQ

User = get_user_model()


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Enforce staff/superuser/admin role for dashboard operations.
    """
    def test_func(self):
        user = self.request.user
        return bool(user.is_authenticated and (
            user.is_staff or
            user.is_superuser or
            getattr(user, 'user_type', None) == 'admin'
        ))

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            from django.contrib import messages
            messages.error(self.request, 'Access restricted to administrative accounts.')
            return redirect('dashboard:home')
        return super().handle_no_permission()


class HomeView(TemplateView):
    """
    Public SwiftDrop homepage with real database stats and featured categories.
    """
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['featured_products'] = ProductService.objects.filter(
            is_available=True
        ).order_by('-created_at')[:8]

        context['recent_reviews'] = Review.objects.filter(
            is_public=True
        ).select_related('customer', 'product').order_by('-created_at')[:4]

        # Real operational metrics
        context['total_products'] = ProductService.objects.filter(is_available=True).count()
        context['total_orders'] = Order.objects.count()
        context['delivered_orders'] = Order.objects.filter(status='delivered').count()
        context['total_zones'] = DeliveryArea.objects.filter(is_active=True).count()

        # Category highlights
        context['categories'] = ProductService.CATEGORY_CHOICES

        return context


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """
    Comprehensive operational command center for SwiftDrop administrators.
    """
    template_name = 'dashboard/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # 1. Orders Breakdown
        all_orders = Order.objects.all()
        context['total_orders'] = all_orders.count()
        context['pending_orders'] = all_orders.filter(status='pending').count()
        context['confirmed_orders'] = all_orders.filter(status='confirmed').count()
        context['processing_orders'] = all_orders.filter(status='processing').count()
        context['dispatched_orders'] = all_orders.filter(status='dispatched').count()
        context['delivered_orders'] = all_orders.filter(status='delivered').count()
        context['cancelled_orders'] = all_orders.filter(status='cancelled').count()

        # 2. Real Revenue Statistics
        completed_payments = Payment.objects.filter(status='completed')
        context['total_revenue'] = completed_payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')

        context['weekly_revenue'] = completed_payments.filter(
            created_at__gte=week_ago
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        context['monthly_revenue'] = completed_payments.filter(
            created_at__gte=month_ago
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        context['pending_revenue'] = Payment.objects.filter(
            status='pending'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # 3. User & Fleet Metrics
        context['total_customers'] = User.objects.filter(user_type='customer').count()
        context['total_agents'] = User.objects.filter(user_type='delivery_agent').count()
        context['available_agents'] = User.objects.filter(
            user_type='delivery_agent',
            delivery_agent_profile__is_available=True
        ).count()

        # 4. Catalog Metrics
        context['total_products'] = ProductService.objects.count()
        context['out_of_stock_count'] = ProductService.objects.filter(stock_quantity=0).count()

        # 5. Recent Activity
        context['recent_orders'] = Order.objects.select_related(
            'customer'
        ).order_by('-created_at')[:10]

        context['recent_reviews'] = Review.objects.select_related(
            'customer', 'product'
        ).order_by('-created_at')[:5]

        # 6. Delivery areas
        context['delivery_areas'] = DeliveryArea.objects.all().order_by('name')

        context['last_updated'] = now
        return context


class AdminPanelView(AdminRequiredMixin, TemplateView):
    """
    Catalog and zone inventory management panel.
    """
    template_name = 'dashboard/admin_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = ProductService.objects.all().order_by('-created_at')
        context['categories'] = ProductService.CATEGORY_CHOICES
        context['delivery_areas'] = DeliveryArea.objects.all().order_by('name')
        context['total_products'] = ProductService.objects.count()
        context['active_products'] = ProductService.objects.filter(is_available=True).count()
        context['low_stock_products'] = ProductService.objects.filter(stock_quantity__lte=5)
        return context


class UserDashboardView(LoginRequiredMixin, TemplateView):
    """
    Personal account overview for customers.
    """
    template_name = 'users/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        user_orders = Order.objects.filter(customer=user)
        context['total_orders'] = user_orders.count()
        context['pending_orders'] = user_orders.filter(status='pending').count()
        context['in_transit_orders'] = user_orders.filter(status='dispatched').count()
        context['delivered_orders'] = user_orders.filter(status='delivered').count()
        context['cancelled_orders'] = user_orders.filter(status='cancelled').count()

        context['recent_orders'] = user_orders.order_by('-created_at')[:5]

        context['total_spent'] = Payment.objects.filter(
            order__customer=user,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Fix: customer=user instead of user=user
        context['user_reviews'] = Review.objects.filter(
            customer=user
        ).select_related('product', 'order').order_by('-created_at')[:4]

        return context


class FAQListView(ListView):
    """
    Customer FAQs and support questions.
    """
    model = FAQ
    template_name = 'dashboard/faq.html'
    context_object_name = 'faqs'

    def get_queryset(self):
        return FAQ.objects.filter(is_active=True).order_by('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = FAQ.CATEGORY_CHOICES
        return context


class ContactView(TemplateView):
    """
    Contact and customer care directory.
    """
    template_name = 'dashboard/contact.html'

    def post(self, request, *args, **kwargs):
        from django.contrib import messages
        messages.success(request, 'Thank you for reaching out! A SwiftDrop care specialist will contact you shortly.')
        return render(request, self.template_name)


class TermsView(TemplateView):
    template_name = 'dashboard/terms.html'


class PrivacyView(TemplateView):
    template_name = 'dashboard/privacy.html'

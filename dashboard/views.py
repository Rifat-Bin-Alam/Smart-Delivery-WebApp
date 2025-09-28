from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from orders.models import Order, ProductService
from payments.models import Payment
from delivery.models import DeliveryAssignment
from reviews.models import Review
from .models import Notification, AnalyticsData, FAQ

User = get_user_model()


class TestView(TemplateView):
    """
    Simple test view to verify server is working
    """
    template_name = 'test.html'


class DatabaseViewerView(TemplateView):
    """
    Database viewer to see all data
    """
    template_name = 'dashboard/database_viewer.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            from django.contrib.auth import get_user_model
            from orders.models import ProductService, Order
            from django.utils import timezone
            
            User = get_user_model()
            
            context['users'] = User.objects.all()
            context['products'] = ProductService.objects.all()
            context['orders'] = Order.objects.all()
            context['now'] = timezone.now()
        except Exception as e:
            context['users'] = []
            context['products'] = []
            context['orders'] = []
            context['now'] = timezone.now()
        
        return context


class NotificationStreamView(TemplateView):
    """
    Notification stream view for real-time updates
    """
    template_name = 'dashboard/notifications.html'
    
    def get(self, request, *args, **kwargs):
        # Return a simple JSON response for now
        from django.http import JsonResponse
        return JsonResponse({
            'notifications': [],
            'status': 'success',
            'message': 'No new notifications'
        })


class HomeView(TemplateView):
    """
    Home page view with real-time data based on user type
    """
    template_name = 'dashboard/simple_home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Get featured products
            context['featured_products'] = ProductService.objects.filter(is_available=True)[:6]
            
            # Get recent reviews
            context['recent_reviews'] = Review.objects.filter(is_public=True).order_by('-created_at')[:5]
            
            # Get statistics - real-time data
            context['total_products'] = ProductService.objects.filter(is_available=True).count()
            context['total_orders'] = Order.objects.count()
            context['total_customers'] = User.objects.filter(user_type='customer').count()
            context['total_delivery_agents'] = User.objects.filter(user_type='delivery_agent').count()
            
            # Add real-time timestamp
            context['last_updated'] = timezone.now()
            
        except Exception as e:
            # Fallback values if there are any issues
            context['featured_products'] = []
            context['recent_reviews'] = []
            context['total_products'] = 0
            context['total_orders'] = 0
            context['total_customers'] = 0
            context['total_delivery_agents'] = 0
            context['last_updated'] = timezone.now()
        
        return context


class AdminDashboardView(TemplateView):
    """
    Admin dashboard view with real-time analytics
    """
    template_name = 'dashboard/admin_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Real-time admin statistics
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # Order statistics
            context['total_orders'] = Order.objects.count()
            context['pending_orders'] = Order.objects.filter(status='pending').count()
            context['completed_orders'] = Order.objects.filter(status='delivered').count()
            context['cancelled_orders'] = Order.objects.filter(status='cancelled').count()
            
            # Recent orders
            context['recent_orders'] = Order.objects.all().order_by('-created_at')[:10]
            
            # Revenue statistics
            context['total_revenue'] = Payment.objects.filter(status='completed').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            context['weekly_revenue'] = Payment.objects.filter(
                status='completed',
                created_at__date__gte=week_ago
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            context['monthly_revenue'] = Payment.objects.filter(
                status='completed',
                created_at__date__gte=month_ago
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Customer statistics
            context['total_customers'] = User.objects.filter(user_type='customer').count()
            context['new_customers_week'] = User.objects.filter(
                user_type='customer',
                date_joined__date__gte=week_ago
            ).count()
            
            # Product statistics
            context['total_products'] = ProductService.objects.count()
            context['available_products'] = ProductService.objects.filter(is_available=True).count()
            
            context['last_updated'] = timezone.now()
            
        except Exception as e:
            # Fallback values
            context['total_orders'] = 0
            context['pending_orders'] = 0
            context['completed_orders'] = 0
            context['cancelled_orders'] = 0
            context['recent_orders'] = []
            context['total_revenue'] = 0
            context['weekly_revenue'] = 0
            context['monthly_revenue'] = 0
            context['total_customers'] = 0
            context['new_customers_week'] = 0
            context['total_products'] = 0
            context['available_products'] = 0
            context['last_updated'] = timezone.now()
        
        return context


class UserDashboardView(LoginRequiredMixin, TemplateView):
    """
    User-specific dashboard view with real-time data
    """
    template_name = 'users/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            # User-specific order statistics
            user_orders = Order.objects.filter(customer=user)
            context['total_orders'] = user_orders.count()
            context['pending_orders'] = user_orders.filter(status='pending').count()
            context['completed_orders'] = user_orders.filter(status='delivered').count()
            context['cancelled_orders'] = user_orders.filter(status='cancelled').count()
            
            # Recent orders for this user
            context['recent_orders'] = user_orders.order_by('-created_at')[:5]
            
            # Total amount spent
            context['total_spent'] = Payment.objects.filter(
                order__customer=user,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # User's reviews
            context['user_reviews'] = Review.objects.filter(user=user).order_by('-created_at')[:3]
            
            context['last_updated'] = timezone.now()
            
        except Exception as e:
            # Fallback values
            context['total_orders'] = 0
            context['pending_orders'] = 0
            context['completed_orders'] = 0
            context['cancelled_orders'] = 0
            context['recent_orders'] = []
            context['total_spent'] = 0
            context['user_reviews'] = []
            context['last_updated'] = timezone.now()
        
        return context


class AdminPanelView(TemplateView):
    """
    Admin panel view for analytics and system management (NO ORDERING)
    """
    template_name = 'dashboard/admin_panel.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Get all products for management
            context['products'] = ProductService.objects.all().order_by('-created_at')
            
            # Get date ranges
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # Order statistics for analysis
            context['total_orders'] = Order.objects.count()
            context['pending_orders'] = Order.objects.filter(status='pending').count()
            context['completed_orders'] = Order.objects.filter(status='delivered').count()
            context['cancelled_orders'] = Order.objects.filter(status='cancelled').count()
            
            # Revenue statistics for analysis
            context['total_revenue'] = Payment.objects.filter(status='completed').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            context['weekly_revenue'] = Payment.objects.filter(
                status='completed',
                created_at__date__gte=week_ago
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            context['monthly_revenue'] = Payment.objects.filter(
                status='completed',
                created_at__date__gte=month_ago
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Customer statistics for analysis
            context['total_customers'] = User.objects.filter(user_type='customer').count()
            context['new_customers_week'] = User.objects.filter(
                user_type='customer',
                date_joined__date__gte=week_ago
            ).count()
            
            # Delivery statistics for analysis
            context['total_deliveries'] = DeliveryAssignment.objects.count()
            context['completed_deliveries'] = DeliveryAssignment.objects.filter(
                actual_delivery_time__isnull=False
            ).count()
            
            # Recent orders for analysis (read-only)
            context['recent_orders'] = Order.objects.all().order_by('-created_at')[:10]
            
            # Recent payments
            context['recent_payments'] = Payment.objects.order_by('-created_at')[:10]
            
            # Top products
            context['top_products'] = ProductService.objects.annotate(
                order_count=Count('orderitem__order')
            ).order_by('-order_count')[:5]
            
        except Exception as e:
            # Fallback values if there are any issues
            context['products'] = []
            context['orders'] = []
            context['total_orders'] = 0
            context['pending_orders'] = 0
            context['completed_orders'] = 0
            context['cancelled_orders'] = 0
            context['total_revenue'] = 0
            context['weekly_revenue'] = 0
            context['monthly_revenue'] = 0
            context['total_customers'] = 0
            context['new_customers_week'] = 0
            context['total_deliveries'] = 0
            context['completed_deliveries'] = 0
            context['recent_orders'] = []
            context['recent_payments'] = []
            context['top_products'] = []
        
        return context


class AnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Analytics view
    """
    template_name = 'dashboard/analytics.html'
    
    def test_func(self):
        return self.request.user.is_admin
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get analytics data for the last 30 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Order analytics
        orders_by_date = Order.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        context['orders_by_date'] = list(orders_by_date)
        
        # Revenue analytics
        revenue_by_date = Payment.objects.filter(
            status='completed',
            created_at__date__range=[start_date, end_date]
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(total=Sum('amount')).order_by('day')
        
        context['revenue_by_date'] = list(revenue_by_date)
        
        # Product category analytics
        category_stats = ProductService.objects.values('category').annotate(
            count=Count('id'),
            total_orders=Count('orderitem__order')
        ).order_by('-total_orders')
        
        context['category_stats'] = list(category_stats)
        
        return context


class NotificationListView(LoginRequiredMixin, ListView):
    """
    Notification list view
    """
    model = Notification
    template_name = 'dashboard/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')


class MarkNotificationReadView(LoginRequiredMixin, TemplateView):
    """
    Mark notification as read
    """
    def post(self, request, *args, **kwargs):
        notification = Notification.objects.get(
            pk=kwargs['pk'],
            recipient=request.user
        )
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return JsonResponse({'success': True})


class FAQListView(ListView):
    """
    FAQ list view
    """
    model = FAQ
    template_name = 'dashboard/faq.html'
    context_object_name = 'faqs'
    
    def get_queryset(self):
        return FAQ.objects.filter(is_active=True).order_by('order', 'question')


class ContactView(TemplateView):
    """
    Contact page view
    """
    template_name = 'dashboard/contact.html'


class ReportsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Reports view
    """
    template_name = 'dashboard/reports.html'
    
    def test_func(self):
        return self.request.user.is_admin


class OrderReportView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Order report view
    """
    template_name = 'dashboard/order_report.html'
    
    def test_func(self):
        return self.request.user.is_admin
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from query parameters
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date and end_date:
            orders = Order.objects.filter(
                created_at__date__range=[start_date, end_date]
            )
        else:
            # Default to last 30 days
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
            orders = Order.objects.filter(
                created_at__date__range=[start_date, end_date]
            )
        
        context['orders'] = orders.order_by('-created_at')
        context['start_date'] = start_date
        context['end_date'] = end_date
        
        return context


class RevenueReportView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Revenue report view
    """
    template_name = 'dashboard/revenue_report.html'
    
    def test_func(self):
        return self.request.user.is_admin
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from query parameters
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date and end_date:
            payments = Payment.objects.filter(
                status='completed',
                created_at__date__range=[start_date, end_date]
            )
        else:
            # Default to last 30 days
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
            payments = Payment.objects.filter(
                status='completed',
                created_at__date__range=[start_date, end_date]
            )
        
        context['payments'] = payments.order_by('-created_at')
        context['total_revenue'] = payments.aggregate(total=Sum('amount'))['total'] or 0
        context['start_date'] = start_date
        context['end_date'] = end_date
        
        return context


class DeliveryReportView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Delivery report view
    """
    template_name = 'dashboard/delivery_report.html'
    
    def test_func(self):
        return self.request.user.is_admin
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from query parameters
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date and end_date:
            deliveries = DeliveryAssignment.objects.filter(
                assigned_at__date__range=[start_date, end_date]
            )
        else:
            # Default to last 30 days
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
            deliveries = DeliveryAssignment.objects.filter(
                assigned_at__date__range=[start_date, end_date]
            )
        
        context['deliveries'] = deliveries.order_by('-assigned_at')
        context['start_date'] = start_date
        context['end_date'] = end_date
        
        return context
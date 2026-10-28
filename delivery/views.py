from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from decimal import Decimal
import json

from .models import DeliveryAssignment, DeliveryStatus, DeliveryArea, DeliveryAgentLocation, DeliveryRating
from orders.models import Order, OrderStatusHistory
from payments.models import Payment
from django.contrib.auth import get_user_model

User = get_user_model()


class DeliveryAgentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Enforce delivery partner or staff access.
    """
    def test_func(self):
        user = self.request.user
        return bool(user.is_authenticated and (
            user.is_staff or
            user.is_superuser or
            getattr(user, 'user_type', None) in ('delivery_agent', 'admin')
        ))

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Access restricted to authorized delivery partners.')
            return redirect('dashboard:home')
        return super().handle_no_permission()


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return bool(user.is_authenticated and (
            user.is_staff or
            user.is_superuser or
            getattr(user, 'user_type', None) == 'admin'
        ))

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Administrative access required.')
            return redirect('dashboard:home')
        return super().handle_no_permission()


class MyDeliveriesView(DeliveryAgentRequiredMixin, ListView):
    """
    Delivery Partner workspace showing active assignments and delivery history.
    """
    model = DeliveryAssignment
    template_name = 'delivery/my_deliveries.html'
    context_object_name = 'deliveries'
    paginate_by = 15

    def get_queryset(self):
        user = self.request.user
        queryset = DeliveryAssignment.objects.filter(
            delivery_agent=user
        ).select_related('order', 'order__customer').order_by('-assigned_at')

        tab = self.request.GET.get('tab', 'active')
        if tab == 'active':
            queryset = queryset.exclude(order__status__in=['delivered', 'cancelled', 'returned'])
        elif tab == 'completed':
            queryset = queryset.filter(order__status='delivered')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['active_tab'] = self.request.GET.get('tab', 'active')

        # Agent profile and stats
        profile = getattr(user, 'delivery_agent_profile', None)
        context['agent_profile'] = profile
        context['total_completed'] = DeliveryAssignment.objects.filter(
            delivery_agent=user,
            order__status='delivered'
        ).count()
        context['active_count'] = DeliveryAssignment.objects.filter(
            delivery_agent=user
        ).exclude(order__status__in=['delivered', 'cancelled', 'returned']).count()

        return context


class MyDeliveryDetailView(DeliveryAgentRequiredMixin, DetailView):
    """
    Detailed delivery task page for the assigned rider.
    """
    model = DeliveryAssignment
    template_name = 'delivery/my_delivery_detail.html'
    context_object_name = 'assignment'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'user_type', None) == 'admin':
            return DeliveryAssignment.objects.all()
        return DeliveryAssignment.objects.filter(delivery_agent=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignment = self.object
        order = assignment.order
        context['order'] = order
        context['items'] = order.items.select_related('product').all()
        context['payments'] = order.payments.all()
        context['updates'] = assignment.status_updates.order_by('-timestamp')
        return context


class DeliveryStatusUpdateView(DeliveryAgentRequiredMixin, TemplateView):
    """
    Status advancement for riders: Picked Up, In Transit, Delivered.
    """
    def post(self, request, *args, **kwargs):
        user = request.user
        assignment = get_object_or_404(DeliveryAssignment, pk=kwargs['pk'])

        # Enforce assignment ownership
        if assignment.delivery_agent != user and not (user.is_staff or getattr(user, 'user_type', None) == 'admin'):
            messages.error(request, 'You are not authorized to update this delivery task.')
            return redirect('delivery:my_deliveries')

        action = request.POST.get('action')
        notes = request.POST.get('notes', '').strip()
        location_text = request.POST.get('location', '').strip()
        order = assignment.order

        if action == 'pickup':
            assignment.status_updates.create(
                status='picked_up',
                location=location_text or 'Merchant Dispatch',
                notes=notes or 'Package picked up by rider.'
            )
            order.status = 'dispatched'
            order.save()
            OrderStatusHistory.objects.create(
                order=order,
                status='dispatched',
                notes=f"Picked up by rider {user.get_full_name() or user.username}.",
                created_by=user
            )
            messages.success(request, f"Order #{order.order_number} marked as Picked Up & Out for Delivery.")

        elif action == 'in_transit':
            assignment.status_updates.create(
                status='in_transit',
                location=location_text or 'En Route to Delivery Address',
                notes=notes or 'Rider is in transit towards customer location.'
            )
            messages.success(request, f"Transit update recorded for order #{order.order_number}.")

        elif action == 'deliver':
            assignment.status_updates.create(
                status='delivered',
                location=location_text or order.delivery_address,
                notes=notes or 'Package handed over to customer.'
            )
            assignment.actual_delivery_time = timezone.now()
            assignment.save()

            order.status = 'delivered'
            order.save()

            # Complete any pending COD payments
            for payment in order.payments.filter(status='pending'):
                payment.status = 'completed'
                payment.paid_at = timezone.now()
                payment.save()

            # Update agent delivery stats
            if hasattr(user, 'delivery_agent_profile') and user.delivery_agent_profile:
                user.delivery_agent_profile.total_deliveries += 1
                user.delivery_agent_profile.save()

            OrderStatusHistory.objects.create(
                order=order,
                status='delivered',
                notes=f"Delivery completed and confirmed by rider {user.get_full_name() or user.username}.",
                created_by=user
            )
            messages.success(request, f"Congratulations! Order #{order.order_number} has been marked as Delivered.")

        return redirect('delivery:my_delivery_detail', pk=assignment.pk)


class LocationUpdateView(DeliveryAgentRequiredMixin, TemplateView):
    """
    Simulated or browser-reported location ping for riders.
    """
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            lat = Decimal(str(data.get('latitude', '23.8103')))
            lng = Decimal(str(data.get('longitude', '90.4125')))
            address_note = str(data.get('address', 'Simulated Rider Location Ping')).strip()

            DeliveryAgentLocation.objects.create(
                delivery_agent=request.user,
                latitude=lat,
                longitude=lng,
                address=address_note
            )
            return JsonResponse({'success': True, 'message': 'Location ping logged successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)


class DeliveryAreaListView(ListView):
    """
    Public listing of serviceable zones and standard delivery rates.
    """
    model = DeliveryArea
    template_name = 'delivery/delivery_area_list.html'
    context_object_name = 'areas'

    def get_queryset(self):
        return DeliveryArea.objects.filter(is_active=True).order_by('delivery_fee')


class DeliveryRateView(LoginRequiredMixin, CreateView):
    """
    Customer rating for their delivery partner after successful delivery.
    """
    model = DeliveryRating
    fields = ['rating', 'comment']
    template_name = 'delivery/delivery_rate.html'

    def form_valid(self, form):
        assignment = get_object_or_404(DeliveryAssignment, pk=self.kwargs['pk'])
        if assignment.order.customer != self.request.user:
            messages.error(self.request, 'You may only rate deliveries for your own orders.')
            return redirect('orders:order_list')

        form.instance.delivery_assignment = assignment
        response = super().form_valid(form)

        # Recalculate agent average rating
        agent_profile = getattr(assignment.delivery_agent, 'delivery_agent_profile', None)
        if agent_profile:
            ratings = DeliveryRating.objects.filter(delivery_assignment__delivery_agent=assignment.delivery_agent)
            if ratings.exists():
                avg = sum(r.rating for r in ratings) / ratings.count()
                agent_profile.rating = round(avg, 1)
                agent_profile.save()

        messages.success(self.request, 'Thank you! Your delivery rating has been submitted.')
        return response

    def get_success_url(self):
        return reverse('orders:order_detail', kwargs={'pk': self.object.delivery_assignment.order.pk})


# Administrative views
class AdminDeliveryListView(AdminRequiredMixin, ListView):
    model = DeliveryAssignment
    template_name = 'delivery/admin_delivery_list.html'
    context_object_name = 'deliveries'
    paginate_by = 20

    def get_queryset(self):
        return DeliveryAssignment.objects.all().select_related(
            'order', 'delivery_agent', 'delivery_agent__delivery_agent_profile'
        ).order_by('-assigned_at')


class AdminDeliveryAgentListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'delivery/admin_delivery_agent_list.html'
    context_object_name = 'delivery_agents'
    paginate_by = 20

    def get_queryset(self):
        return User.objects.filter(
            user_type='delivery_agent'
        ).select_related('delivery_agent_profile').order_by('-date_joined')

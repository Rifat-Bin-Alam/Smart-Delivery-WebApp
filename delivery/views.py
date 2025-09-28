from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .models import DeliveryAssignment, DeliveryStatus, DeliveryArea, DeliveryAgentLocation, DeliveryRating

User = get_user_model()

class DeliveryListView(LoginRequiredMixin, ListView):
    """
    Delivery list view
    """
    model = DeliveryAssignment
    template_name = 'delivery/delivery_list.html'
    context_object_name = 'deliveries'
    paginate_by = 20
    
    def get_queryset(self):
        if self.request.user.is_admin:
            return DeliveryAssignment.objects.all().order_by('-assigned_at')
        elif self.request.user.is_delivery_agent:
            return DeliveryAssignment.objects.filter(delivery_agent=self.request.user).order_by('-assigned_at')
        else:
            return DeliveryAssignment.objects.none()


class DeliveryDetailView(LoginRequiredMixin, DetailView):
    """
    Delivery detail view
    """
    model = DeliveryAssignment
    template_name = 'delivery/delivery_detail.html'
    context_object_name = 'delivery'


class MyDeliveriesView(LoginRequiredMixin, ListView):
    """
    My deliveries view for delivery agents
    """
    model = DeliveryAssignment
    template_name = 'delivery/my_deliveries.html'
    context_object_name = 'deliveries'
    paginate_by = 20
    
    def get_queryset(self):
        return DeliveryAssignment.objects.filter(delivery_agent=self.request.user).order_by('-assigned_at')


class MyDeliveryDetailView(LoginRequiredMixin, DetailView):
    """
    My delivery detail view for delivery agents
    """
    model = DeliveryAssignment
    template_name = 'delivery/my_delivery_detail.html'
    context_object_name = 'delivery'
    
    def get_queryset(self):
        return DeliveryAssignment.objects.filter(delivery_agent=self.request.user)


class DeliveryAreaListView(ListView):
    """
    Delivery area list view
    """
    model = DeliveryArea
    template_name = 'delivery/delivery_area_list.html'
    context_object_name = 'areas'
    
    def get_queryset(self):
        return DeliveryArea.objects.filter(is_active=True).order_by('name')


class DeliveryAreaDetailView(DetailView):
    """
    Delivery area detail view
    """
    model = DeliveryArea
    template_name = 'delivery/delivery_area_detail.html'
    context_object_name = 'area'


class DeliveryRateView(LoginRequiredMixin, CreateView):
    """
    Delivery rating view
    """
    model = DeliveryRating
    template_name = 'delivery/delivery_rate.html'
    fields = ['rating', 'comment']
    success_url = reverse_lazy('delivery:my_deliveries')
    
    def form_valid(self, form):
        delivery_assignment = get_object_or_404(DeliveryAssignment, pk=self.kwargs['pk'])
        form.instance.delivery_assignment = delivery_assignment
        response = super().form_valid(form)
        messages.success(self.request, 'রেটিং সফলভাবে দেওয়া হয়েছে।')
        return response


class DeliveryRatingListView(ListView):
    """
    Delivery rating list view
    """
    model = DeliveryRating
    template_name = 'delivery/delivery_rating_list.html'
    context_object_name = 'ratings'
    paginate_by = 20
    
    def get_queryset(self):
        return DeliveryRating.objects.all().order_by('-rated_at')


# Admin views
class AdminDeliveryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Admin delivery list view
    """
    model = DeliveryAssignment
    template_name = 'delivery/admin_delivery_list.html'
    context_object_name = 'deliveries'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_admin
    
    def get_queryset(self):
        return DeliveryAssignment.objects.all().order_by('-assigned_at')


class AdminDeliveryAssignView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Admin delivery assign view
    """
    template_name = 'delivery/admin_delivery_assign.html'
    
    def test_func(self):
        return self.request.user.is_admin


class AdminDeliveryAgentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Admin delivery agent list view
    """
    model = User
    template_name = 'delivery/admin_delivery_agent_list.html'
    context_object_name = 'delivery_agents'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_admin
    
    def get_queryset(self):
        return User.objects.filter(user_type='delivery_agent').order_by('-date_joined')


class AdminDeliveryAgentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Admin delivery agent detail view
    """
    model = User
    template_name = 'delivery/admin_delivery_agent_detail.html'
    context_object_name = 'delivery_agent'
    
    def test_func(self):
        return self.request.user.is_admin
    
    def get_queryset(self):
        return User.objects.filter(user_type='delivery_agent')


class AdminAssignDeliveryView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Admin assign delivery view
    """
    template_name = 'delivery/admin_assign_delivery.html'
    
    def test_func(self):
        return self.request.user.is_admin


# Status update views
class DeliveryStatusUpdateView(LoginRequiredMixin, TemplateView):
    """
    Delivery status update view
    """
    template_name = 'delivery/delivery_status_update.html'


class DeliveryPickupView(LoginRequiredMixin, TemplateView):
    """
    Delivery pickup view
    """
    template_name = 'delivery/delivery_pickup.html'


class DeliveryDeliverView(LoginRequiredMixin, TemplateView):
    """
    Delivery deliver view
    """
    template_name = 'delivery/delivery_deliver.html'


class DeliveryCompleteView(LoginRequiredMixin, TemplateView):
    """
    Delivery complete view
    """
    template_name = 'delivery/delivery_complete.html'


# Location tracking views
class LocationUpdateView(LoginRequiredMixin, TemplateView):
    """
    Location update view
    """
    template_name = 'delivery/location_update.html'


class LocationHistoryView(LoginRequiredMixin, ListView):
    """
    Location history view
    """
    model = DeliveryAgentLocation
    template_name = 'delivery/location_history.html'
    context_object_name = 'locations'
    paginate_by = 20
    
    def get_queryset(self):
        return DeliveryAgentLocation.objects.filter(delivery_agent=self.request.user).order_by('-timestamp')
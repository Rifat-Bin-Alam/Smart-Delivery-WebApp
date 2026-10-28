from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, TemplateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.db import models
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    UserProfileForm,
    CustomerProfileForm,
    DeliveryAgentProfileForm,
    DeliveryAgentSignupForm,
)
from .models import CustomerProfile, DeliveryAgentProfile

User = get_user_model()


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin to enforce admin / staff access.
    """
    def test_func(self):
        return bool(self.request.user.is_authenticated and (
            self.request.user.is_staff or
            self.request.user.is_superuser or
            getattr(self.request.user, 'user_type', None) == 'admin'
        ))

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Access restricted to administrative accounts.')
            return redirect('dashboard:home')
        return super().handle_no_permission()


class LoginView(TemplateView):
    """
    User login view supporting email or username.
    """
    template_name = 'users/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff or getattr(request.user, 'user_type', None) == 'admin':
                return redirect('dashboard:admin_dashboard')
            elif getattr(request.user, 'user_type', None) == 'delivery_agent':
                return redirect('delivery:my_deliveries')
            return redirect('dashboard:home')
        form = CustomAuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            display_name = user.get_full_name() or user.username
            messages.success(request, f'Welcome back, {display_name}!')

            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)

            if user.is_staff or user.is_superuser or getattr(user, 'user_type', None) == 'admin':
                return redirect('dashboard:admin_dashboard')
            elif getattr(user, 'user_type', None) == 'delivery_agent':
                return redirect('delivery:my_deliveries')
            return redirect('dashboard:home')

        messages.error(request, 'Invalid email/username or password. Please try again.')
        return render(request, self.template_name, {'form': form})


class LogoutView(TemplateView):
    """
    User logout view.
    """
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('dashboard:home')

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('dashboard:home')


class UserDashboardView(LoginRequiredMixin, TemplateView):
    """
    User dashboard view with real activity metrics.
    """
    template_name = 'users/dashboard.html'

    def get_context_data(self, **kwargs):
        from decimal import Decimal
        from django.db.models import Sum
        from orders.models import Order
        from payments.models import Payment
        from reviews.models import Review

        context = super().get_context_data(**kwargs)
        user = self.request.user

        user_orders = Order.objects.filter(customer=user)
        context['total_orders'] = user_orders.count()
        context['pending_orders'] = user_orders.filter(status='pending').count()
        context['in_transit_orders'] = user_orders.filter(status__in=['processing', 'dispatched']).count()
        context['delivered_orders'] = user_orders.filter(status='delivered').count()
        context['cancelled_orders'] = user_orders.filter(status='cancelled').count()
        context['recent_orders'] = user_orders.order_by('-created_at')[:6]

        context['total_spent'] = Payment.objects.filter(
            order__customer=user,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        context['user_reviews'] = Review.objects.filter(
            customer=user
        ).select_related('product', 'order').order_by('-created_at')[:4]

        return context


class SignupView(TemplateView):
    """
    User signup view.
    """
    template_name = 'users/signup.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        form = CustomUserCreationForm()
        form.fields['user_type'].initial = 'customer'
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Your SwiftDrop account has been created successfully! Please sign in.')
                return redirect('users:login')
            except Exception as e:
                messages.error(request, f'Account creation failed: {str(e)}')
        else:
            for field, errors in form.errors.items():
                field_label = form.fields[field].label if field in form.fields else field
                for error in errors:
                    messages.error(request, f'{field_label}: {error}')

        return render(request, self.template_name, {'form': form})


class DeliveryAgentSignupView(CreateView):
    """
    Delivery agent signup view.
    """
    model = User
    form_class = DeliveryAgentSignupForm
    template_name = 'users/delivery_agent_signup.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Delivery partner account created successfully! Please sign in.')
        return response


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    User profile view.
    """
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_customer:
            try:
                context['customer_profile'] = user.customer_profile
            except CustomerProfile.DoesNotExist:
                context['customer_profile'] = None
        elif user.is_delivery_agent:
            try:
                context['delivery_agent_profile'] = user.delivery_agent_profile
            except DeliveryAgentProfile.DoesNotExist:
                context['delivery_agent_profile'] = None

        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """
    User profile edit view.
    """
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your profile has been updated successfully.')
        return response


class UserListView(AdminRequiredMixin, ListView):
    """
    User list view (Admin only).
    """
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                models.Q(username__icontains=q) |
                models.Q(email__icontains=q) |
                models.Q(first_name__icontains=q) |
                models.Q(last_name__icontains=q) |
                models.Q(phone_number__icontains=q)
            )
        role = self.request.GET.get('role')
        if role in ('customer', 'admin', 'delivery_agent'):
            queryset = queryset.filter(user_type=role)
        return queryset


class UserDetailView(AdminRequiredMixin, DetailView):
    """
    User detail view (Admin only).
    """
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user_detail'


class DeliveryAgentListView(AdminRequiredMixin, ListView):
    """
    Delivery agent list view (Admin only).
    """
    model = User
    template_name = 'users/delivery_agent_list.html'
    context_object_name = 'delivery_agents'
    paginate_by = 20

    def get_queryset(self):
        return User.objects.filter(user_type='delivery_agent').order_by('-date_joined')


class DeliveryAgentDetailView(AdminRequiredMixin, DetailView):
    """
    Delivery agent detail view (Admin only).
    """
    model = User
    template_name = 'users/delivery_agent_detail.html'
    context_object_name = 'delivery_agent'

    def get_queryset(self):
        return User.objects.filter(user_type='delivery_agent')


class UserEditView(AdminRequiredMixin, UpdateView):
    """
    User edit view (Admin only).
    """
    model = User
    form_class = UserProfileForm
    template_name = 'users/user_edit.html'
    success_url = reverse_lazy('users:user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'User {self.object.get_full_name() or self.object.username} updated successfully.')
        return response


class UserDeleteView(AdminRequiredMixin, DeleteView):
    """
    User delete view (Admin only).
    """
    model = User
    template_name = 'users/user_delete.html'
    success_url = reverse_lazy('users:user_list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'User deleted successfully.')
        return response


class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    """
    Account self-deletion view.
    """
    model = User
    template_name = 'users/profile_delete.html'
    success_url = reverse_lazy('dashboard:home')

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Your account has been deleted.')
        return response


from django.contrib.auth.views import (
    PasswordChangeView as BasePasswordChangeView,
    PasswordChangeDoneView as BasePasswordChangeDoneView,
    PasswordResetView as BasePasswordResetView,
    PasswordResetDoneView as BasePasswordResetDoneView,
    PasswordResetConfirmView as BasePasswordResetConfirmView,
    PasswordResetCompleteView as BasePasswordResetCompleteView,
)


class PasswordChangeView(LoginRequiredMixin, BasePasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:password_change_done')


class PasswordChangeDoneView(LoginRequiredMixin, BasePasswordChangeDoneView):
    template_name = 'users/password_change_done.html'


class PasswordResetView(BasePasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')


class PasswordResetDoneView(BasePasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class PasswordResetConfirmView(BasePasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class PasswordResetCompleteView(BasePasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'


class EmailVerificationView(LoginRequiredMixin, TemplateView):
    template_name = 'users/email_verification.html'


class EmailVerificationConfirmView(TemplateView):
    template_name = 'users/email_verification_confirm.html'


class ToggleAvailabilityView(LoginRequiredMixin, TemplateView):
    """
    Toggle delivery agent availability.
    """
    def post(self, request, *args, **kwargs):
        agent_id = kwargs.get('pk')
        if not (request.user.is_staff or request.user.pk == agent_id):
            messages.error(request, 'You do not have permission to modify this status.')
            return redirect('dashboard:home')

        delivery_agent = get_object_or_404(User, pk=agent_id, user_type='delivery_agent')
        try:
            profile = delivery_agent.delivery_agent_profile
            profile.is_available = not profile.is_available
            profile.save()

            status_str = 'Available' if profile.is_available else 'Offline'
            messages.success(request, f'Delivery status updated to: {status_str}')
        except DeliveryAgentProfile.DoesNotExist:
            messages.error(request, 'Delivery profile not found.')

        if request.user.user_type == 'delivery_agent':
            return redirect('delivery:my_deliveries')
        return redirect('users:delivery_agent_detail', pk=delivery_agent.pk)

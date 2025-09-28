from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, CustomerProfileForm, DeliveryAgentProfileForm, DeliveryAgentSignupForm
from .models import CustomerProfile, DeliveryAgentProfile

User = get_user_model()


class LoginView(TemplateView):
    """
    User login view
    """
    template_name = 'users/login.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        form = CustomAuthenticationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        print(f"DEBUG: Login attempt - Username: {request.POST.get('username')}")
        form = CustomAuthenticationForm(data=request.POST)
        print(f"DEBUG: Form valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"DEBUG: Form errors: {form.errors}")
        
        if form.is_valid():
            user = form.get_user()
            print(f"DEBUG: User found: {user}")
            login(request, user)
            messages.success(request, f'স্বাগতম, {user.get_full_name() or user.username}!')
            return redirect('dashboard:home')
        return render(request, self.template_name, {'form': form})


class LogoutView(TemplateView):
    """
    User logout view
    """
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'সফলভাবে লগআউট হয়েছে।')
        return redirect('dashboard:home')


class UserDashboardView(TemplateView):
    """
    User dashboard view
    """
    template_name = 'users/dashboard.html'


class SignupView(TemplateView):
    """
    User signup view
    """
    template_name = 'users/signup.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        form = CustomUserCreationForm()
        # Ensure user_type is set to customer by default
        form.fields['user_type'].initial = 'customer'
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        print(f"DEBUG: Signup attempt - Username: {request.POST.get('username')}")
        form = CustomUserCreationForm(data=request.POST)
        print(f"DEBUG: Form valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"DEBUG: Form errors: {form.errors}")
            # Show specific error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label}: {error}')
        else:
            try:
                user = form.save()
                print(f"DEBUG: User created: {user.username}")
                messages.success(request, 'আপনার অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে। দয়া করে লগইন করুন।')
                return redirect('users:login')
            except Exception as e:
                print(f"DEBUG: Error creating user: {e}")
                messages.error(request, f'অ্যাকাউন্ট তৈরি করতে সমস্যা হয়েছে: {str(e)}')
        
        return render(request, self.template_name, {'form': form})




class DeliveryAgentSignupView(CreateView):
    """
    Delivery agent signup view
    """
    model = User
    form_class = DeliveryAgentSignupForm
    template_name = 'users/delivery_agent_signup.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'ডেলিভারি এজেন্ট অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে। দয়া করে লগইন করুন।')
        return response


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    User profile view
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
    User profile edit view
    """
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'আপনার প্রোফাইল সফলভাবে আপডেট হয়েছে।')
        return response


class UserListView(LoginRequiredMixin, ListView):
    """
    User list view (admin only)
    """
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')


class UserDetailView(LoginRequiredMixin, DetailView):
    """
    User detail view (admin only)
    """
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user_detail'


class DeliveryAgentListView(LoginRequiredMixin, ListView):
    """
    Delivery agent list view
    """
    model = User
    template_name = 'users/delivery_agent_list.html'
    context_object_name = 'delivery_agents'
    paginate_by = 20
    
    def get_queryset(self):
        return User.objects.filter(user_type='delivery_agent').order_by('-date_joined')


class DeliveryAgentDetailView(LoginRequiredMixin, DetailView):
    """
    Delivery agent detail view
    """
    model = User
    template_name = 'users/delivery_agent_detail.html'
    context_object_name = 'delivery_agent'
    
    def get_queryset(self):
        return User.objects.filter(user_type='delivery_agent')


# Password management views
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


# Email verification views
class EmailVerificationView(LoginRequiredMixin, TemplateView):
    template_name = 'users/email_verification.html'


class EmailVerificationConfirmView(TemplateView):
    template_name = 'users/email_verification_confirm.html'


# Additional views for admin functionality
class UserEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/user_edit.html'
    success_url = reverse_lazy('users:user_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'ব্যবহারকারী {self.object.get_full_name()} সফলভাবে আপডেট হয়েছে।')
        return response


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'users/user_delete.html'
    success_url = reverse_lazy('users:user_list')
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'ব্যবহারকারী সফলভাবে মুছে ফেলা হয়েছে।')
        return response


class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    """
    Profile delete view
    """
    model = User
    template_name = 'users/profile_delete.html'
    success_url = reverse_lazy('dashboard:home')
    
    def get_object(self):
        return self.request.user
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'আপনার অ্যাকাউন্ট সফলভাবে মুছে ফেলা হয়েছে।')
        return response


class ToggleAvailabilityView(LoginRequiredMixin, TemplateView):
    """
    Toggle delivery agent availability
    """
    def post(self, request, *args, **kwargs):
        delivery_agent = User.objects.get(pk=kwargs['pk'], user_type='delivery_agent')
        try:
            profile = delivery_agent.delivery_agent_profile
            profile.is_available = not profile.is_available
            profile.save()
            
            status = 'উপলব্ধ' if profile.is_available else 'অনুপলব্ধ'
            messages.success(request, f'ডেলিভারি এজেন্ট {status} হিসেবে চিহ্নিত হয়েছে।')
        except DeliveryAgentProfile.DoesNotExist:
            messages.error(request, 'ডেলিভারি এজেন্ট প্রোফাইল পাওয়া যায়নি।')
        
        return redirect('users:delivery_agent_detail', pk=delivery_agent.pk)

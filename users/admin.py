from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, CustomerProfile, DeliveryAgentProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin with Bengali support
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'phone_number', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('ব্যক্তিগত তথ্য'), {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        (_('অনুমতি'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('অতিরিক্ত তথ্য'), {'fields': ('user_type', 'address', 'city', 'postal_code', 'profile_picture', 'is_verified', 'last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone_number', 'user_type', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined')


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    """
    Customer Profile Admin
    """
    list_display = ('user', 'preferred_language', 'emergency_contact')
    list_filter = ('preferred_language',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    
    fieldsets = (
        (_('গ্রাহক তথ্য'), {
            'fields': ('user', 'preferred_language', 'emergency_contact', 'delivery_instructions')
        }),
    )


@admin.register(DeliveryAgentProfile)
class DeliveryAgentProfileAdmin(admin.ModelAdmin):
    """
    Delivery Agent Profile Admin
    """
    list_display = ('user', 'license_number', 'vehicle_type', 'vehicle_number', 'is_available', 'rating', 'total_deliveries')
    list_filter = ('vehicle_type', 'is_available', 'rating')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'license_number', 'vehicle_number')
    readonly_fields = ('rating', 'total_deliveries')
    
    fieldsets = (
        (_('এজেন্ট তথ্য'), {
            'fields': ('user', 'license_number', 'vehicle_type', 'vehicle_number')
        }),
        (_('অবস্থা'), {
            'fields': ('is_available', 'rating', 'total_deliveries')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

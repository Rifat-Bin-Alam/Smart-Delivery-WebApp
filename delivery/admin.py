from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import DeliveryAssignment, DeliveryStatus, DeliveryArea, DeliveryAgentLocation, DeliveryRating


class DeliveryStatusInline(admin.TabularInline):
    model = DeliveryStatus
    extra = 0
    readonly_fields = ('timestamp',)
    fields = ('status', 'location', 'notes', 'timestamp')


@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    """
    Delivery Assignment Admin
    """
    list_display = ('order', 'delivery_agent', 'assigned_at', 'estimated_delivery_time', 'actual_delivery_time')
    list_filter = ('assigned_at', 'delivery_agent__user_type')
    search_fields = ('order__order_number', 'delivery_agent__username', 'delivery_agent__first_name')
    readonly_fields = ('assigned_at',)
    inlines = [DeliveryStatusInline]
    
    fieldsets = (
        (_('নির্ধারণ তথ্য'), {
            'fields': ('order', 'delivery_agent', 'assigned_by', 'assigned_at')
        }),
        (_('সময়'), {
            'fields': ('estimated_delivery_time', 'actual_delivery_time')
        }),
        (_('নোট'), {
            'fields': ('delivery_notes',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'delivery_agent', 'assigned_by')


@admin.register(DeliveryStatus)
class DeliveryStatusAdmin(admin.ModelAdmin):
    """
    Delivery Status Admin
    """
    list_display = ('delivery_assignment', 'status', 'location', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('delivery_assignment__order__order_number', 'delivery_assignment__delivery_agent__username')
    readonly_fields = ('timestamp',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('delivery_assignment__order', 'delivery_assignment__delivery_agent')


@admin.register(DeliveryArea)
class DeliveryAreaAdmin(admin.ModelAdmin):
    """
    Delivery Area Admin
    """
    list_display = ('name', 'delivery_fee', 'estimated_delivery_time', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (_('এলাকা তথ্য'), {
            'fields': ('name', 'description', 'is_active')
        }),
        (_('ফি ও সময়'), {
            'fields': ('delivery_fee', 'estimated_delivery_time')
        }),
        (_('সময়'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(DeliveryAgentLocation)
class DeliveryAgentLocationAdmin(admin.ModelAdmin):
    """
    Delivery Agent Location Admin
    """
    list_display = ('delivery_agent', 'address', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('delivery_agent__username', 'delivery_agent__first_name', 'address')
    readonly_fields = ('timestamp',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('delivery_agent')


@admin.register(DeliveryRating)
class DeliveryRatingAdmin(admin.ModelAdmin):
    """
    Delivery Rating Admin
    """
    list_display = ('delivery_assignment', 'rating', 'rated_at')
    list_filter = ('rating', 'rated_at')
    search_fields = ('delivery_assignment__order__order_number', 'delivery_assignment__delivery_agent__username')
    readonly_fields = ('rated_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('delivery_assignment__order', 'delivery_assignment__delivery_agent')
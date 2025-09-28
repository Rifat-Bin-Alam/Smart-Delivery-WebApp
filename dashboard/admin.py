from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import DashboardWidget, AnalyticsData, Notification, SystemLog, FAQ


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    """
    Dashboard Widget Admin
    """
    list_display = ('name', 'widget_type', 'is_active', 'position', 'created_at')
    list_filter = ('widget_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'position')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (_('উইজেট তথ্য'), {
            'fields': ('name', 'widget_type', 'description', 'is_active', 'position')
        }),
        (_('কনফিগারেশন'), {
            'fields': ('config',),
            'classes': ('collapse',)
        }),
        (_('সময়'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(AnalyticsData)
class AnalyticsDataAdmin(admin.ModelAdmin):
    """
    Analytics Data Admin
    """
    list_display = ('metric_type', 'date', 'value', 'created_at')
    list_filter = ('metric_type', 'date', 'created_at')
    search_fields = ('metric_type',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (_('মেট্রিক তথ্য'), {
            'fields': ('metric_type', 'date', 'value')
        }),
        (_('মেটাডেটা'), {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        (_('সময়'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Notification Admin
    """
    list_display = ('title', 'recipient', 'notification_type', 'priority', 'is_read', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'created_at')
    search_fields = ('title', 'recipient__username', 'recipient__first_name')
    readonly_fields = ('created_at', 'read_at')
    
    fieldsets = (
        (_('নোটিফিকেশন তথ্য'), {
            'fields': ('title', 'message', 'notification_type', 'priority', 'recipient')
        }),
        (_('অবস্থা'), {
            'fields': ('is_read', 'read_at')
        }),
        (_('অ্যাকশন'), {
            'fields': ('action_url',)
        }),
        (_('মেটাডেটা'), {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        (_('সময়'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient')


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    """
    System Log Admin
    """
    list_display = ('user', 'action', 'model_name', 'level', 'created_at')
    list_filter = ('action', 'level', 'created_at')
    search_fields = ('user__username', 'model_name', 'message')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (_('লগ তথ্য'), {
            'fields': ('user', 'action', 'model_name', 'object_id', 'message', 'level')
        }),
        (_('নেটওয়ার্ক'), {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        (_('মেটাডেটা'), {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        (_('সময়'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """
    FAQ Admin
    """
    list_display = ('question', 'category', 'is_active', 'order', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('question', 'answer')
    list_editable = ('is_active', 'order')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('প্রশ্নোত্তর'), {
            'fields': ('question', 'answer', 'category', 'is_active', 'order')
        }),
        (_('সময়'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import ProductService, Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)
    fields = ('product', 'quantity', 'unit_price', 'total_price')


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('status', 'notes', 'created_by', 'created_at')


@admin.register(ProductService)
class ProductServiceAdmin(admin.ModelAdmin):
    """
    Product/Service Admin
    """
    list_display = ('name', 'category', 'price', 'stock_quantity', 'is_available', 'created_at')
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_available', 'stock_quantity')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('মূল তথ্য'), {
            'fields': ('name', 'description', 'category', 'price', 'is_available')
        }),
        (_('স্টক ও ছবি'), {
            'fields': ('stock_quantity', 'image')
        }),
        (_('সময়'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Order Admin
    """
    list_display = ('order_number', 'customer', 'delivery_type', 'status', 'total_amount', 'cancelled_at', 'created_at')
    list_filter = ('status', 'delivery_type', 'created_at', 'delivery_city', 'cancelled_at')
    search_fields = ('order_number', 'customer__username', 'customer__first_name', 'customer__last_name', 'delivery_address', 'cancellation_reason')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'cancelled_at')
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        (_('অর্ডার তথ্য'), {
            'fields': ('order_number', 'customer', 'delivery_type', 'scheduled_delivery_time')
        }),
        (_('ডেলিভারি তথ্য'), {
            'fields': ('delivery_address', 'delivery_city', 'delivery_instructions')
        }),
        (_('অবস্থা ও পরিমাণ'), {
            'fields': ('status', 'total_amount', 'delivery_fee', 'special_instructions')
        }),
        (_('বাতিলের তথ্য'), {
            'fields': ('cancellation_reason', 'cancellation_notes', 'cancelled_at', 'cancelled_by', 'refund_preference'),
            'classes': ('collapse',)
        }),
        (_('সময়'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer').prefetch_related('items')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Order Item Admin
    """
    list_display = ('order', 'product', 'quantity', 'unit_price', 'total_price')
    list_filter = ('product__category',)
    search_fields = ('order__order_number', 'product__name')
    readonly_fields = ('total_price',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'product')


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """
    Order Status History Admin
    """
    list_display = ('order', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'created_by__username')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'created_by')
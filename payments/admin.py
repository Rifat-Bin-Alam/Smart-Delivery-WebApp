from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Payment, PaymentMethod, PaymentTransaction, Refund


class PaymentTransactionInline(admin.TabularInline):
    model = PaymentTransaction
    extra = 0
    readonly_fields = ('timestamp',)
    fields = ('action', 'status', 'message', 'timestamp')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Payment Admin
    """
    list_display = ('transaction_id', 'order', 'payment_method', 'amount', 'status', 'created_at')
    list_filter = ('payment_method', 'status', 'created_at')
    search_fields = ('transaction_id', 'order__order_number', 'payment_reference')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at', 'paid_at')
    inlines = [PaymentTransactionInline]
    
    fieldsets = (
        (_('পেমেন্ট তথ্য'), {
            'fields': ('order', 'payment_method', 'amount', 'status', 'transaction_id', 'payment_reference')
        }),
        (_('পেমেন্ট বিবরণ'), {
            'fields': ('payment_details',),
            'classes': ('collapse',)
        }),
        (_('সময়'), {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """
    Payment Method Admin
    """
    list_display = ('name', 'code', 'is_active', 'processing_fee', 'min_amount', 'max_amount')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    list_editable = ('is_active',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (_('মূল তথ্য'), {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        (_('ছবি'), {
            'fields': ('icon',)
        }),
        (_('ফি ও সীমা'), {
            'fields': ('processing_fee', 'min_amount', 'max_amount')
        }),
        (_('সময়'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    """
    Payment Transaction Admin
    """
    list_display = ('payment', 'action', 'status', 'timestamp')
    list_filter = ('action', 'status', 'timestamp')
    search_fields = ('payment__transaction_id', 'payment__order__order_number')
    readonly_fields = ('timestamp',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payment__order')


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """
    Refund Admin
    """
    list_display = ('payment', 'amount', 'status', 'reason', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('payment__transaction_id', 'payment__order__order_number', 'refund_reference')
    readonly_fields = ('created_at', 'processed_at')
    
    fieldsets = (
        (_('রিফান্ড তথ্য'), {
            'fields': ('payment', 'amount', 'reason', 'status', 'refund_reference')
        }),
        (_('প্রক্রিয়াকরণ'), {
            'fields': ('processed_by', 'processed_at')
        }),
        (_('সময়'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payment__order', 'processed_by')
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Review, ReviewImage, ReviewHelpful, ReviewResponse, ReviewReport


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0
    fields = ('image', 'caption')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Review Admin
    """
    list_display = ('customer', 'product', 'order', 'rating', 'is_verified', 'is_public', 'helpful_count', 'created_at')
    list_filter = ('rating', 'is_verified', 'is_public', 'created_at', 'product__category')
    search_fields = ('customer__username', 'customer__first_name', 'product__name', 'order__order_number')
    readonly_fields = ('helpful_count', 'created_at', 'updated_at')
    inlines = [ReviewImageInline]
    
    fieldsets = (
        (_('রিভিউ তথ্য'), {
            'fields': ('customer', 'order', 'product', 'rating', 'title', 'comment')
        }),
        (_('অবস্থা'), {
            'fields': ('is_verified', 'is_public', 'helpful_count')
        }),
        (_('সময়'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'order', 'product')


@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    """
    Review Image Admin
    """
    list_display = ('review', 'caption', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('review__customer__username', 'review__product__name')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('review__customer', 'review__product')


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    """
    Review Helpful Admin
    """
    list_display = ('review', 'user', 'is_helpful', 'created_at')
    list_filter = ('is_helpful', 'created_at')
    search_fields = ('review__customer__username', 'user__username')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('review__customer', 'user')


@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    """
    Review Response Admin
    """
    list_display = ('review', 'responder', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('review__customer__username', 'responder__username')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('review__customer', 'responder')


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    """
    Review Report Admin
    """
    list_display = ('review', 'reporter', 'reason', 'status', 'created_at')
    list_filter = ('reason', 'status', 'created_at')
    search_fields = ('review__customer__username', 'reporter__username')
    readonly_fields = ('created_at', 'reviewed_at')
    
    fieldsets = (
        (_('রিপোর্ট তথ্য'), {
            'fields': ('review', 'reporter', 'reason', 'description', 'status')
        }),
        (_('পর্যালোচনা'), {
            'fields': ('reviewed_by', 'reviewed_at')
        }),
        (_('সময়'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('review__customer', 'reporter', 'reviewed_by')
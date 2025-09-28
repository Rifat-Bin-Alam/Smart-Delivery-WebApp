from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardWidget(models.Model):
    """
    Model for customizable dashboard widgets
    """
    WIDGET_TYPES = [
        ('chart', 'চার্ট'),
        ('table', 'টেবিল'),
        ('metric', 'মেট্রিক'),
        ('list', 'তালিকা'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('নাম')
    )
    
    widget_type = models.CharField(
        max_length=20,
        choices=WIDGET_TYPES,
        verbose_name=_('উইজেট ধরন')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('বিবরণ')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('সক্রিয়')
    )
    
    position = models.PositiveIntegerField(
        default=0,
        verbose_name=_('অবস্থান')
    )
    
    config = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('কনফিগারেশন')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('তৈরি হয়েছে')
    )
    
    class Meta:
        verbose_name = _('ড্যাশবোর্ড উইজেট')
        verbose_name_plural = _('ড্যাশবোর্ড উইজেট')
        ordering = ['position', 'name']
    
    def __str__(self):
        return self.name


class AnalyticsData(models.Model):
    """
    Model for storing analytics data
    """
    METRIC_TYPES = [
        ('orders', 'অর্ডার'),
        ('revenue', 'রাজস্ব'),
        ('customers', 'গ্রাহক'),
        ('deliveries', 'ডেলিভারি'),
        ('products', 'পণ্য'),
        ('reviews', 'রিভিউ'),
    ]
    
    metric_type = models.CharField(
        max_length=20,
        choices=METRIC_TYPES,
        verbose_name=_('মেট্রিক ধরন')
    )
    
    date = models.DateField(
        verbose_name=_('তারিখ')
    )
    
    value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name=_('মান')
    )
    
    metadata = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('মেটাডেটা')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('তৈরি হয়েছে')
    )
    
    class Meta:
        verbose_name = _('এনালিটিক্স ডেটা')
        verbose_name_plural = _('এনালিটিক্স ডেটা')
        ordering = ['-date', 'metric_type']
        unique_together = ['metric_type', 'date']
    
    def __str__(self):
        return f"{self.get_metric_type_display()} - {self.date} - {self.value}"


class Notification(models.Model):
    """
    Model for system notifications
    """
    NOTIFICATION_TYPES = [
        ('order', 'অর্ডার'),
        ('delivery', 'ডেলিভারি'),
        ('payment', 'পেমেন্ট'),
        ('review', 'রিভিউ'),
        ('system', 'সিস্টেম'),
        ('promotion', 'প্রমোশন'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'নিম্ন'),
        ('medium', 'মধ্যম'),
        ('high', 'উচ্চ'),
        ('urgent', 'জরুরি'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('শিরোনাম')
    )
    
    message = models.TextField(
        verbose_name=_('বার্তা')
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        verbose_name=_('নোটিফিকেশন ধরন')
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_('অগ্রাধিকার')
    )
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('প্রাপক')
    )
    
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('পড়া হয়েছে')
    )
    
    read_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('পড়া হয়েছে')
    )
    
    action_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('অ্যাকশন URL')
    )
    
    metadata = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('মেটাডেটা')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('তৈরি হয়েছে')
    )
    
    class Meta:
        verbose_name = _('নোটিফিকেশন')
        verbose_name_plural = _('নোটিফিকেশন')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.get_full_name()}"


class SystemLog(models.Model):
    """
    Model for system activity logs
    """
    LOG_LEVELS = [
        ('debug', 'ডিবাগ'),
        ('info', 'তথ্য'),
        ('warning', 'সতর্কতা'),
        ('error', 'ত্রুটি'),
        ('critical', 'ক্রিটিক্যাল'),
    ]
    
    ACTION_TYPES = [
        ('create', 'তৈরি'),
        ('read', 'পড়া'),
        ('update', 'আপডেট'),
        ('delete', 'মুছে ফেলা'),
        ('login', 'লগইন'),
        ('logout', 'লগআউট'),
        ('error', 'ত্রুটি'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_logs',
        verbose_name=_('ব্যবহারকারী')
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name=_('কর্ম')
    )
    
    model_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('মডেল নাম')
    )
    
    object_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('অবজেক্ট ID')
    )
    
    message = models.TextField(
        verbose_name=_('বার্তা')
    )
    
    level = models.CharField(
        max_length=10,
        choices=LOG_LEVELS,
        default='info',
        verbose_name=_('লেভেল')
    )
    
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_('IP ঠিকানা')
    )
    
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ইউজার এজেন্ট')
    )
    
    metadata = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('মেটাডেটা')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('তৈরি হয়েছে')
    )
    
    class Meta:
        verbose_name = _('সিস্টেম লগ')
        verbose_name_plural = _('সিস্টেম লগ')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.model_name} - {self.created_at}"


class FAQ(models.Model):
    """
    Model for Frequently Asked Questions
    """
    CATEGORY_CHOICES = [
        ('general', 'সাধারণ'),
        ('orders', 'অর্ডার'),
        ('delivery', 'ডেলিভারি'),
        ('payment', 'পেমেন্ট'),
        ('account', 'অ্যাকাউন্ট'),
        ('technical', 'প্রযুক্তিগত'),
    ]
    
    question = models.CharField(
        max_length=500,
        verbose_name=_('প্রশ্ন')
    )
    
    answer = models.TextField(
        verbose_name=_('উত্তর')
    )
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name=_('বিভাগ')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('সক্রিয়')
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('ক্রম')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('তৈরি হয়েছে')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('আপডেট হয়েছে')
    )
    
    class Meta:
        verbose_name = _('প্রায়শই জিজ্ঞাসিত প্রশ্ন')
        verbose_name_plural = _('প্রায়শই জিজ্ঞাসিত প্রশ্ন')
        ordering = ['order', 'question']
    
    def __str__(self):
        return self.question
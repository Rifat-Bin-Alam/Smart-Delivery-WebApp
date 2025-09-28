from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    Supports customers, admins, and delivery agents
    """
    USER_TYPE_CHOICES = [
        ('customer', 'গ্রাহক'),
        ('admin', 'অ্যাডমিন'),
        ('delivery_agent', 'ডেলিভারি এজেন্ট'),
    ]
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='customer',
        verbose_name=_('ব্যবহারকারীর ধরন')
    )
    
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        verbose_name=_('ফোন নম্বর')
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ঠিকানা')
    )
    
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('শহর')
    )
    
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name=_('পোস্টাল কোড')
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name=_('প্রোফাইল ছবি')
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('যাচাইকৃত')
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
        verbose_name = _('ব্যবহারকারী')
        verbose_name_plural = _('ব্যবহারকারীরা')
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"
    
    def get_user_type_display(self):
        return dict(self.USER_TYPE_CHOICES)[self.user_type]
    
    @property
    def is_customer(self):
        return self.user_type == 'customer'
    
    @property
    def is_admin(self):
        return self.user_type == 'admin'
    
    @property
    def is_delivery_agent(self):
        return self.user_type == 'delivery_agent'


class CustomerProfile(models.Model):
    """
    Extended profile for customers
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer_profile',
        verbose_name=_('ব্যবহারকারী')
    )
    
    preferred_language = models.CharField(
        max_length=10,
        choices=[('bn', 'বাংলা'), ('en', 'English')],
        default='bn',
        verbose_name=_('পছন্দের ভাষা')
    )
    
    emergency_contact = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_('জরুরি যোগাযোগ')
    )
    
    delivery_instructions = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ডেলিভারি নির্দেশনা')
    )
    
    class Meta:
        verbose_name = _('গ্রাহক প্রোফাইল')
        verbose_name_plural = _('গ্রাহক প্রোফাইল')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - গ্রাহক প্রোফাইল"


class DeliveryAgentProfile(models.Model):
    """
    Extended profile for delivery agents
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='delivery_agent_profile',
        verbose_name=_('ব্যবহারকারী')
    )
    
    license_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('লাইসেন্স নম্বর')
    )
    
    vehicle_type = models.CharField(
        max_length=50,
        choices=[
            ('bike', 'বাইক'),
            ('cycle', 'সাইকেল'),
            ('car', 'গাড়ি'),
            ('van', 'ভ্যান'),
        ],
        verbose_name=_('যানবাহনের ধরন')
    )
    
    vehicle_number = models.CharField(
        max_length=20,
        verbose_name=_('যানবাহনের নম্বর')
    )
    
    is_available = models.BooleanField(
        default=True,
        verbose_name=_('উপলব্ধ')
    )
    
    rating = models.FloatField(
        default=0.0,
        verbose_name=_('রেটিং')
    )
    
    total_deliveries = models.PositiveIntegerField(
        default=0,
        verbose_name=_('মোট ডেলিভারি')
    )
    
    class Meta:
        verbose_name = _('ডেলিভারি এজেন্ট প্রোফাইল')
        verbose_name_plural = _('ডেলিভারি এজেন্ট প্রোফাইল')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - ডেলিভারি এজেন্ট"

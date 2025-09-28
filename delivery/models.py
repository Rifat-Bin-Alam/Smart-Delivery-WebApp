from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from orders.models import Order

User = get_user_model()


class DeliveryAssignment(models.Model):
    """
    Model for assigning delivery agents to orders
    """
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='delivery_assignment',
        verbose_name=_('অর্ডার')
    )
    
    delivery_agent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='delivery_assignments',
        limit_choices_to={'user_type': 'delivery_agent'},
        verbose_name=_('ডেলিভারি এজেন্ট')
    )
    
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('নির্ধারিত হয়েছে')
    )
    
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_deliveries',
        verbose_name=_('নির্ধারিত করেছেন')
    )
    
    estimated_delivery_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('আনুমানিক ডেলিভারি সময়')
    )
    
    actual_delivery_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('প্রকৃত ডেলিভারি সময়')
    )
    
    delivery_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ডেলিভারি নোট')
    )
    
    class Meta:
        verbose_name = _('ডেলিভারি নির্ধারণ')
        verbose_name_plural = _('ডেলিভারি নির্ধারণ')
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"অর্ডার #{self.order.order_number} - {self.delivery_agent.get_full_name()}"


class DeliveryStatus(models.Model):
    """
    Model for tracking delivery status updates
    """
    STATUS_CHOICES = [
        ('assigned', 'নির্ধারিত'),
        ('picked_up', 'পিকআপ সম্পন্ন'),
        ('in_transit', 'পথে'),
        ('delivered', 'ডেলিভারি সম্পন্ন'),
        ('failed', 'ব্যর্থ'),
        ('returned', 'ফেরত'),
    ]
    
    delivery_assignment = models.ForeignKey(
        DeliveryAssignment,
        on_delete=models.CASCADE,
        related_name='status_updates',
        verbose_name=_('ডেলিভারি নির্ধারণ')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name=_('অবস্থা')
    )
    
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('অবস্থান')
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('নোট')
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('সময়')
    )
    
    class Meta:
        verbose_name = _('ডেলিভারি অবস্থা')
        verbose_name_plural = _('ডেলিভারি অবস্থা')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.delivery_assignment.order.order_number} - {self.get_status_display()}"


class DeliveryArea(models.Model):
    """
    Model for defining delivery areas and zones
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('নাম')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('বিবরণ')
    )
    
    delivery_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('ডেলিভারি ফি (৳)')
    )
    
    estimated_delivery_time = models.PositiveIntegerField(
        help_text='Estimated delivery time in minutes',
        verbose_name=_('আনুমানিক ডেলিভারি সময় (মিনিট)')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('সক্রিয়')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('তৈরি হয়েছে')
    )
    
    class Meta:
        verbose_name = _('ডেলিভারি এলাকা')
        verbose_name_plural = _('ডেলিভারি এলাকা')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - ৳{self.delivery_fee}"


class DeliveryAgentLocation(models.Model):
    """
    Model for tracking delivery agent locations
    """
    delivery_agent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='locations',
        limit_choices_to={'user_type': 'delivery_agent'},
        verbose_name=_('ডেলিভারি এজেন্ট')
    )
    
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_('অক্ষাংশ')
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_('দ্রাঘিমাংশ')
    )
    
    address = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('ঠিকানা')
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('সময়')
    )
    
    class Meta:
        verbose_name = _('ডেলিভারি এজেন্ট অবস্থান')
        verbose_name_plural = _('ডেলিভারি এজেন্ট অবস্থান')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.delivery_agent.get_full_name()} - {self.timestamp}"


class DeliveryRating(models.Model):
    """
    Model for rating delivery agents
    """
    delivery_assignment = models.OneToOneField(
        DeliveryAssignment,
        on_delete=models.CASCADE,
        related_name='rating',
        verbose_name=_('ডেলিভারি নির্ধারণ')
    )
    
    rating = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ],
        verbose_name=_('রেটিং (1-5)')
    )
    
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('মন্তব্য')
    )
    
    rated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('রেটিং দেওয়া হয়েছে')
    )
    
    class Meta:
        verbose_name = _('ডেলিভারি রেটিং')
        verbose_name_plural = _('ডেলিভারি রেটিং')
    
    def __str__(self):
        return f"{self.delivery_assignment.order.order_number} - {self.rating}⭐"
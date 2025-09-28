from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from orders.models import Order

User = get_user_model()


class Payment(models.Model):
    """
    Model for payment transactions
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash_on_delivery', 'ক্যাশ অন ডেলিভারি'),
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('rocket', 'Rocket'),
        ('bank_transfer', 'ব্যাংক ট্রান্সফার'),
        ('card', 'কার্ড'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'অপেক্ষমান'),
        ('processing', 'প্রক্রিয়াধীন'),
        ('completed', 'সম্পন্ন'),
        ('failed', 'ব্যর্থ'),
        ('cancelled', 'বাতিল'),
        ('refunded', 'ফেরত'),
    ]
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('অর্ডার')
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name=_('পেমেন্ট পদ্ধতি')
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('পরিমাণ (৳)')
    )
    
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name=_('অবস্থা')
    )
    
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_('লেনদেন আইডি')
    )
    
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('পেমেন্ট রেফারেন্স')
    )
    
    payment_details = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('পেমেন্ট বিবরণ')
    )
    
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('পেমেন্ট দেওয়া হয়েছে')
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
        verbose_name = _('পেমেন্ট')
        verbose_name_plural = _('পেমেন্ট')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"পেমেন্ট #{self.id} - অর্ডার #{self.order.order_number} - ৳{self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            import uuid
            self.transaction_id = f"TXN{str(uuid.uuid4())[:12].upper()}"
        super().save(*args, **kwargs)


class PaymentMethod(models.Model):
    """
    Model for available payment methods
    """
    name = models.CharField(
        max_length=50,
        verbose_name=_('নাম')
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('কোড')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('সক্রিয়')
    )
    
    icon = models.ImageField(
        upload_to='payment_methods/',
        blank=True,
        null=True,
        verbose_name=_('আইকন')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('বিবরণ')
    )
    
    processing_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('প্রসেসিং ফি (৳)')
    )
    
    min_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('ন্যূনতম পরিমাণ (৳)')
    )
    
    max_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_('সর্বোচ্চ পরিমাণ (৳)')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('তৈরি হয়েছে')
    )
    
    class Meta:
        verbose_name = _('পেমেন্ট পদ্ধতি')
        verbose_name_plural = _('পেমেন্ট পদ্ধতি')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PaymentTransaction(models.Model):
    """
    Model for detailed payment transaction logs
    """
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_('পেমেন্ট')
    )
    
    action = models.CharField(
        max_length=50,
        verbose_name=_('কর্ম')
    )
    
    status = models.CharField(
        max_length=20,
        verbose_name=_('অবস্থা')
    )
    
    message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('বার্তা')
    )
    
    response_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('প্রতিক্রিয়া ডেটা')
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('সময়')
    )
    
    class Meta:
        verbose_name = _('পেমেন্ট লেনদেন')
        verbose_name_plural = _('পেমেন্ট লেনদেন')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.payment} - {self.action} - {self.timestamp}"


class Refund(models.Model):
    """
    Model for handling refunds
    """
    REFUND_STATUS_CHOICES = [
        ('pending', 'অপেক্ষমান'),
        ('processing', 'প্রক্রিয়াধীন'),
        ('completed', 'সম্পন্ন'),
        ('failed', 'ব্যর্থ'),
        ('cancelled', 'বাতিল'),
    ]
    
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='refunds',
        verbose_name=_('পেমেন্ট')
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('পরিমাণ (৳)')
    )
    
    reason = models.TextField(
        verbose_name=_('কারণ')
    )
    
    status = models.CharField(
        max_length=20,
        choices=REFUND_STATUS_CHOICES,
        default='pending',
        verbose_name=_('অবস্থা')
    )
    
    refund_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('রিফান্ড রেফারেন্স')
    )
    
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('প্রক্রিয়াকরণ করেছেন')
    )
    
    processed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('প্রক্রিয়াকরণ হয়েছে')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('তৈরি হয়েছে')
    )
    
    class Meta:
        verbose_name = _('রিফান্ড')
        verbose_name_plural = _('রিফান্ড')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"রিফান্ড #{self.id} - ৳{self.amount} - {self.get_status_display()}"
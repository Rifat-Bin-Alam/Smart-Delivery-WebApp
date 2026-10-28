from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from orders.models import Order
import uuid

User = get_user_model()


class Payment(models.Model):
    """
    Model for order payment records and transactions.
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash_on_delivery', 'Cash on Delivery (COD)'),
        ('bkash', 'bKash Mobile Wallet'),
        ('nagad', 'Nagad Mobile Wallet'),
        ('rocket', 'Rocket Mobile Wallet'),
        ('bank_transfer', 'Direct Bank Transfer'),
        ('card', 'Debit / Credit Card'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('Order')
    )

    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash_on_delivery',
        verbose_name=_('Payment Method')
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Amount (৳)')
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name=_('Payment Status')
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_('Transaction ID')
    )

    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Payment Reference')
    )

    payment_details = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('Payment Metadata')
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Paid At')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment #{self.id} - Order #{self.order.order_number} - ৳{self.amount} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class PaymentMethod(models.Model):
    """
    Model for active payment channels and settings.
    """
    name = models.CharField(
        max_length=50,
        verbose_name=_('Method Name')
    )

    code = models.CharField(
        max_length=30,
        unique=True,
        verbose_name=_('Channel Code')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )

    icon = models.ImageField(
        upload_to='payment_methods/',
        blank=True,
        null=True,
        verbose_name=_('Icon')
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Instructions / Description')
    )

    processing_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        verbose_name=_('Processing Fee (৳)')
    )

    min_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        verbose_name=_('Minimum Amount (৳)')
    )

    max_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_('Maximum Amount (৳)')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )

    class Meta:
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        ordering = ['name']

    def __str__(self):
        return self.name


class PaymentTransaction(models.Model):
    """
    Detailed audit log for payment gateway transactions and events.
    """
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_('Payment')
    )

    action = models.CharField(
        max_length=50,
        verbose_name=_('Action')
    )

    status = models.CharField(
        max_length=30,
        verbose_name=_('Status')
    )

    message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Message')
    )

    response_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('Response Payload')
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Timestamp')
    )

    class Meta:
        verbose_name = _('Payment Audit Transaction')
        verbose_name_plural = _('Payment Audit Transactions')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.payment.transaction_id} - {self.action} ({self.status})"


class Refund(models.Model):
    """
    Model for recording customer refunds.
    """
    REFUND_STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='refunds',
        verbose_name=_('Original Payment')
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Refund Amount (৳)')
    )

    reason = models.TextField(
        verbose_name=_('Reason')
    )

    status = models.CharField(
        max_length=20,
        choices=REFUND_STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )

    refund_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Refund Reference')
    )

    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Processed By')
    )

    processed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Processed At')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )

    class Meta:
        verbose_name = _('Refund')
        verbose_name_plural = _('Refunds')
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund #{self.id} - ৳{self.amount} ({self.get_status_display()})"

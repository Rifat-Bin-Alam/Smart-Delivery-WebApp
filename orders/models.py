from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class ProductService(models.Model):
    """
    Model for products and services offered by Nagaribashi Express
    """
    CATEGORY_CHOICES = [
        ('food', 'খাবার'),
        ('medicine', 'ঔষধ'),
        ('gas', 'গ্যাস'),
        ('groceries', 'মুদি সামগ্রী'),
        ('electronics', 'ইলেকট্রনিক্স'),
        ('clothing', 'পোশাক'),
        ('books', 'বই'),
        ('other', 'অন্যান্য'),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name=_('নাম')
    )
    
    description = models.TextField(
        verbose_name=_('বিবরণ')
    )
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name=_('বিভাগ')
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('দাম (৳)')
    )
    
    is_available = models.BooleanField(
        default=True,
        verbose_name=_('উপলব্ধ')
    )
    
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('স্টক পরিমাণ')
    )
    
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name=_('ছবি')
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
        verbose_name = _('পণ্য/সেবা')
        verbose_name_plural = _('পণ্য/সেবা')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - ৳{self.price}"
    
    def is_in_stock(self, quantity=1):
        """
        Check if product has enough stock for the requested quantity
        """
        return self.is_available and self.stock_quantity >= quantity
    
    def reduce_stock(self, quantity):
        """
        Reduce stock quantity when order is placed
        """
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save()
            return True
        return False
    
    def get_stock_status(self):
        """
        Get stock status message
        """
        if not self.is_available:
            return "পণ্যটি বর্তমানে উপলব্ধ নয়"
        elif self.stock_quantity == 0:
            return "স্টক শেষ"
        elif self.stock_quantity <= 5:
            return f"শুধু {self.stock_quantity}টি অবশিষ্ট"
        else:
            return f"{self.stock_quantity}টি স্টকে আছে"


class Order(models.Model):
    """
    Model for customer orders
    """
    ORDER_STATUS_CHOICES = [
        ('pending', 'অপেক্ষমান'),
        ('confirmed', 'নিশ্চিত'),
        ('processing', 'প্রক্রিয়াধীন'),
        ('dispatched', 'প্রেরিত'),
        ('delivered', 'ডেলিভারি সম্পন্ন'),
        ('cancelled', 'বাতিল'),
        ('returned', 'ফেরত'),
    ]
    
    DELIVERY_TYPE_CHOICES = [
        ('instant', 'তাত্ক্ষণিক'),
        ('scheduled', 'নির্ধারিত সময়'),
    ]
    
    order_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('অর্ডার নম্বর')
    )
    
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('গ্রাহক')
    )
    
    delivery_type = models.CharField(
        max_length=20,
        choices=DELIVERY_TYPE_CHOICES,
        default='instant',
        verbose_name=_('ডেলিভারি ধরন')
    )
    
    scheduled_delivery_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('নির্ধারিত ডেলিভারি সময়')
    )
    
    delivery_address = models.TextField(
        verbose_name=_('ডেলিভারি ঠিকানা')
    )
    
    delivery_city = models.CharField(
        max_length=100,
        verbose_name=_('ডেলিভারি শহর')
    )
    
    delivery_instructions = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ডেলিভারি নির্দেশনা')
    )
    
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending',
        verbose_name=_('অবস্থা')
    )
    
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('মোট পরিমাণ (৳)')
    )
    
    delivery_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('ডেলিভারি ফি (৳)')
    )
    
    special_instructions = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('বিশেষ নির্দেশনা')
    )
    
    # Cancellation fields
    cancellation_reason = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('বাতিলের কারণ')
    )
    
    cancellation_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('বাতিলের নোট')
    )
    
    cancelled_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('বাতিল হয়েছে')
    )
    
    cancelled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_orders',
        verbose_name=_('বাতিল করেছেন')
    )
    
    refund_preference = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name=_('রিফান্ড পছন্দ')
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
        verbose_name = _('অর্ডার')
        verbose_name_plural = _('অর্ডার')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"অর্ডার #{self.order_number} - {self.customer.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = f"NE{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    def can_be_cancelled(self):
        """
        Check if order can be cancelled based on status and timing
        """
        # Orders can only be cancelled if they are pending, confirmed, or processing
        cancellable_statuses = ['pending', 'confirmed', 'processing']
        
        if self.status not in cancellable_statuses:
            return False
        
        # Check if order was created more than 24 hours ago (for processing orders)
        if self.status == 'processing':
            from django.utils import timezone
            from datetime import timedelta
            if timezone.now() - self.created_at > timedelta(hours=24):
                return False
        
        return True
    
    def get_cancellation_deadline(self):
        """
        Get the deadline for cancelling this order
        """
        from django.utils import timezone
        from datetime import timedelta
        
        if self.status in ['pending', 'confirmed']:
            return self.created_at + timedelta(hours=48)  # 48 hours for pending/confirmed
        elif self.status == 'processing':
            return self.created_at + timedelta(hours=24)  # 24 hours for processing
        else:
            return None


class OrderItem(models.Model):
    """
    Model for individual items in an order
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('অর্ডার')
    )
    
    product = models.ForeignKey(
        ProductService,
        on_delete=models.CASCADE,
        verbose_name=_('পণ্য/সেবা')
    )
    
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_('পরিমাণ')
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('একক দাম (৳)')
    )
    
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('মোট দাম (৳)')
    )
    
    class Meta:
        verbose_name = _('অর্ডার আইটেম')
        verbose_name_plural = _('অর্ডার আইটেম')
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """
    Model to track order status changes
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name=_('অর্ডার')
    )
    
    status = models.CharField(
        max_length=20,
        choices=Order.ORDER_STATUS_CHOICES,
        verbose_name=_('অবস্থা')
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('নোট')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('তৈরি হয়েছে')
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('তৈরি করেছেন')
    )
    
    class Meta:
        verbose_name = _('অর্ডার অবস্থা ইতিহাস')
        verbose_name_plural = _('অর্ডার অবস্থা ইতিহাস')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"
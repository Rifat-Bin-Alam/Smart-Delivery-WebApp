from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
import uuid

User = get_user_model()


class ProductService(models.Model):
    """
    Model for products and essentials offered by SwiftDrop.
    """
    CATEGORY_CHOICES = [
        ('food', 'Food & Meals'),
        ('groceries', 'Groceries & Fresh'),
        ('medicine', 'Pharmacy & Health'),
        ('gas', 'LPG Gas'),
        ('electronics', 'Electronics & Accessories'),
        ('clothing', 'Apparel & Lifestyle'),
        ('books', 'Books & Stationery'),
        ('other', 'Other Essentials'),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name=_('Product Name')
    )

    description = models.TextField(
        verbose_name=_('Description')
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='groceries',
        verbose_name=_('Category')
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Price (৳)')
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name=_('Available')
    )

    stock_quantity = models.PositiveIntegerField(
        default=10,
        verbose_name=_('Stock Quantity')
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name=_('Product Image')
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
        verbose_name = _('Product / Service')
        verbose_name_plural = _('Products & Services')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - ৳{self.price}"

    def is_in_stock(self, quantity=1):
        return self.is_available and self.stock_quantity >= quantity

    def reduce_stock(self, quantity):
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save(update_fields=['stock_quantity'])
            return True
        return False

    def restore_stock(self, quantity):
        self.stock_quantity += quantity
        self.save(update_fields=['stock_quantity'])

    def get_stock_status(self):
        if not self.is_available:
            return "Unavailable"
        elif self.stock_quantity == 0:
            return "Out of Stock"
        elif self.stock_quantity <= 5:
            return f"Only {self.stock_quantity} left"
        else:
            return f"{self.stock_quantity} in stock"

    @property
    def image_url(self):
        """
        Returns the uploaded image URL if valid, otherwise falls back to a clean category SVG illustration.
        """
        if self.image:
            try:
                return self.image.url
            except (ValueError, AttributeError):
                pass
        valid_categories = {'food', 'groceries', 'medicine', 'gas', 'electronics', 'documents', 'clothing', 'books'}
        cat = self.category if self.category in valid_categories else 'default'
        return f"/static/images/fallbacks/{cat}.svg"


class Order(models.Model):
    """
    Model for customer delivery orders.
    """
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing / Packed'),
        ('dispatched', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ]

    DELIVERY_TYPE_CHOICES = [
        ('instant', 'Instant Express'),
        ('scheduled', 'Scheduled Delivery'),
    ]

    order_number = models.CharField(
        max_length=24,
        unique=True,
        verbose_name=_('Order Reference')
    )

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('Customer')
    )

    delivery_type = models.CharField(
        max_length=20,
        choices=DELIVERY_TYPE_CHOICES,
        default='instant',
        verbose_name=_('Delivery Option')
    )

    scheduled_delivery_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Scheduled Time')
    )

    delivery_address = models.TextField(
        verbose_name=_('Delivery Address')
    )

    delivery_city = models.CharField(
        max_length=100,
        default='Dhaka',
        verbose_name=_('Delivery Area / City')
    )

    delivery_instructions = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Delivery Instructions')
    )

    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Total Amount (৳)')
    )

    delivery_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=50.00,
        validators=[MinValueValidator(0)],
        verbose_name=_('Delivery Fee (৳)')
    )

    special_instructions = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Special Instructions')
    )

    # Cancellation fields
    cancellation_reason = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Cancellation Reason')
    )

    cancellation_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Cancellation Notes')
    )

    cancelled_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Cancelled At')
    )

    cancelled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_orders',
        verbose_name=_('Cancelled By')
    )

    refund_preference = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Refund Preference')
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
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer.get_full_name() or self.customer.username}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"SD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def can_be_cancelled(self):
        cancellable_statuses = ['pending', 'confirmed', 'processing']
        if self.status not in cancellable_statuses:
            return False

        if self.status == 'processing':
            from django.utils import timezone
            from datetime import timedelta
            if timezone.now() - self.created_at > timedelta(hours=24):
                return False

        return True

    def get_cancellation_deadline(self):
        from datetime import timedelta
        if self.status in ['pending', 'confirmed']:
            return self.created_at + timedelta(hours=48)
        elif self.status == 'processing':
            return self.created_at + timedelta(hours=24)
        return None

    @property
    def subtotal(self):
        items_sum = sum(item.total_price for item in self.items.all())
        return items_sum or (self.total_amount - self.delivery_fee)


class OrderItem(models.Model):
    """
    Model for individual items in an order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Order')
    )

    product = models.ForeignKey(
        ProductService,
        on_delete=models.CASCADE,
        verbose_name=_('Product')
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_('Quantity')
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Unit Price (৳)')
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Total Price (৳)')
    )

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """
    Model to track order status changes.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name=_('Order')
    )

    status = models.CharField(
        max_length=20,
        choices=Order.ORDER_STATUS_CHOICES,
        verbose_name=_('Status')
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notes')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Timestamp')
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Recorded By')
    )

    class Meta:
        verbose_name = _('Order Status History')
        verbose_name_plural = _('Order Status History')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"

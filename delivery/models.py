from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from orders.models import Order

User = get_user_model()


class DeliveryArea(models.Model):
    """
    Model for defining delivery service coverage zones and standard fees.
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('Zone / Area Name')
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Coverage Details')
    )

    delivery_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=50.00,
        validators=[MinValueValidator(0)],
        verbose_name=_('Delivery Fee (৳)')
    )

    estimated_delivery_time = models.PositiveIntegerField(
        default=30,
        help_text='Estimated delivery turnaround time in minutes',
        verbose_name=_('Estimated Time (Minutes)')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active Service')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )

    class Meta:
        verbose_name = _('Delivery Area')
        verbose_name_plural = _('Delivery Areas')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - ৳{self.delivery_fee} ({self.estimated_delivery_time} mins)"


class DeliveryAssignment(models.Model):
    """
    Model for assigning delivery partners to orders.
    """
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='delivery_assignment',
        verbose_name=_('Order')
    )

    delivery_agent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='delivery_assignments',
        limit_choices_to={'user_type': 'delivery_agent'},
        verbose_name=_('Delivery Partner')
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Assigned At')
    )

    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_deliveries',
        verbose_name=_('Assigned By')
    )

    estimated_delivery_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Estimated Delivery Time')
    )

    actual_delivery_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Actual Delivery Time')
    )

    delivery_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Delivery Notes')
    )

    class Meta:
        verbose_name = _('Delivery Assignment')
        verbose_name_plural = _('Delivery Assignments')
        ordering = ['-assigned_at']

    def __str__(self):
        agent_name = self.delivery_agent.get_full_name() or self.delivery_agent.username
        return f"Order #{self.order.order_number} -> {agent_name}"


class DeliveryStatus(models.Model):
    """
    Model for tracking delivery timeline updates.
    """
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit / Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Delivery Failed'),
        ('returned', 'Returned'),
    ]

    delivery_assignment = models.ForeignKey(
        DeliveryAssignment,
        on_delete=models.CASCADE,
        related_name='status_updates',
        verbose_name=_('Delivery Assignment')
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name=_('Status')
    )

    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Current Location')
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notes')
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Timestamp')
    )

    class Meta:
        verbose_name = _('Delivery Status Update')
        verbose_name_plural = _('Delivery Status Updates')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.delivery_assignment.order.order_number} - {self.get_status_display()}"


class DeliveryAgentLocation(models.Model):
    """
    Model for tracking delivery agent location pings.
    """
    delivery_agent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='locations',
        limit_choices_to={'user_type': 'delivery_agent'},
        verbose_name=_('Delivery Partner')
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_('Latitude')
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_('Longitude')
    )

    address = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Approximate Address')
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Timestamp')
    )

    class Meta:
        verbose_name = _('Agent Location Update')
        verbose_name_plural = _('Agent Location Updates')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.delivery_agent.get_full_name() or self.delivery_agent.username} @ {self.timestamp}"


class DeliveryRating(models.Model):
    """
    Model for rating delivery partners.
    """
    delivery_assignment = models.OneToOneField(
        DeliveryAssignment,
        on_delete=models.CASCADE,
        related_name='rating',
        verbose_name=_('Delivery Assignment')
    )

    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Rating (1-5)')
    )

    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Comment')
    )

    rated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Rated At')
    )

    class Meta:
        verbose_name = _('Delivery Partner Rating')
        verbose_name_plural = _('Delivery Partner Ratings')

    def __str__(self):
        return f"{self.delivery_assignment.order.order_number} - {self.rating}★"

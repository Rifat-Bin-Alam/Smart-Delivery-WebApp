from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Supports customers, administrators, and delivery agents.
    """
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Administrator'),
        ('delivery_agent', 'Delivery Partner'),
    ]

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='customer',
        verbose_name=_('User Type')
    )

    phone_number = models.CharField(
        max_length=15,
        unique=True,
        verbose_name=_('Phone Number')
    )

    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Address')
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('City / Area')
    )

    postal_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name=_('Postal Code')
    )

    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name=_('Profile Picture')
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Verified')
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
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        name = self.get_full_name() or self.username
        return f"{name} ({self.get_user_type_display()})"

    @property
    def is_customer(self):
        return self.user_type == 'customer'

    @property
    def is_admin(self):
        return self.user_type == 'admin' or self.is_staff or self.is_superuser

    @property
    def is_delivery_agent(self):
        return self.user_type == 'delivery_agent'


class CustomerProfile(models.Model):
    """
    Extended profile for customers.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer_profile',
        verbose_name=_('User')
    )

    preferred_language = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('bn', 'Bengali')],
        default='en',
        verbose_name=_('Preferred Language')
    )

    emergency_contact = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name=_('Emergency Contact')
    )

    delivery_instructions = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Delivery Instructions')
    )

    class Meta:
        verbose_name = _('Customer Profile')
        verbose_name_plural = _('Customer Profiles')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Customer Profile"


class DeliveryAgentProfile(models.Model):
    """
    Extended profile for delivery agents.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='delivery_agent_profile',
        verbose_name=_('User')
    )

    license_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('License Number')
    )

    vehicle_type = models.CharField(
        max_length=50,
        choices=[
            ('bike', 'Motorcycle'),
            ('cycle', 'Bicycle'),
            ('car', 'Car'),
            ('van', 'Van'),
        ],
        default='bike',
        verbose_name=_('Vehicle Type')
    )

    vehicle_number = models.CharField(
        max_length=20,
        verbose_name=_('Vehicle Number')
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name=_('Available for Deliveries')
    )

    rating = models.FloatField(
        default=5.0,
        verbose_name=_('Rating')
    )

    total_deliveries = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total Deliveries')
    )

    class Meta:
        verbose_name = _('Delivery Agent Profile')
        verbose_name_plural = _('Delivery Agent Profiles')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Delivery Partner"

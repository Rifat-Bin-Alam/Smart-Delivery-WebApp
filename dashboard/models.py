from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardWidget(models.Model):
    """
    Model for customizable dashboard widgets.
    """
    WIDGET_TYPES = [
        ('chart', 'Chart'),
        ('table', 'Table'),
        ('metric', 'Metric Card'),
        ('list', 'List'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name=_('Widget Name')
    )

    widget_type = models.CharField(
        max_length=20,
        choices=WIDGET_TYPES,
        verbose_name=_('Widget Type')
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Description')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )

    position = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Display Position')
    )

    config = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('Configuration')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )

    class Meta:
        verbose_name = _('Dashboard Widget')
        verbose_name_plural = _('Dashboard Widgets')
        ordering = ['position', 'name']

    def __str__(self):
        return self.name


class AnalyticsData(models.Model):
    """
    Model for historical snapshot metrics.
    """
    METRIC_TYPES = [
        ('orders', 'Orders'),
        ('revenue', 'Revenue'),
        ('customers', 'Customers'),
        ('deliveries', 'Deliveries'),
        ('products', 'Products'),
        ('reviews', 'Reviews'),
    ]

    metric_type = models.CharField(
        max_length=20,
        choices=METRIC_TYPES,
        verbose_name=_('Metric Type')
    )

    date = models.DateField(
        verbose_name=_('Date')
    )

    value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name=_('Metric Value')
    )

    metadata = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('Metadata')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )

    class Meta:
        verbose_name = _('Analytics Snapshot')
        verbose_name_plural = _('Analytics Snapshots')
        ordering = ['-date', 'metric_type']
        unique_together = ['metric_type', 'date']

    def __str__(self):
        return f"{self.get_metric_type_display()} - {self.date} - {self.value}"


class Notification(models.Model):
    """
    Model for system notifications.
    """
    NOTIFICATION_TYPES = [
        ('order', 'Order Update'),
        ('delivery', 'Delivery Update'),
        ('payment', 'Payment Notification'),
        ('review', 'Review Notification'),
        ('system', 'System Alert'),
        ('promotion', 'Announcement'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name=_('Title')
    )

    message = models.TextField(
        verbose_name=_('Message Body')
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='system',
        verbose_name=_('Category')
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_('Priority')
    )

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Recipient')
    )

    is_read = models.BooleanField(
        default=False,
        verbose_name=_('Read Status')
    )

    read_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Read At')
    )

    action_url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Target Action Link')
    )

    metadata = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('Payload')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Sent At')
    )

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        recipient_name = self.recipient.get_full_name() or self.recipient.username
        return f"{self.title} -> {recipient_name}"


class SystemLog(models.Model):
    """
    Audit log for actions.
    """
    LOG_LEVELS = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]

    ACTION_TYPES = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('error', 'Exception'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_logs',
        verbose_name=_('User')
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name=_('Action')
    )

    model_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Model')
    )

    object_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Object ID')
    )

    message = models.TextField(
        verbose_name=_('Log Message')
    )

    level = models.CharField(
        max_length=10,
        choices=LOG_LEVELS,
        default='info',
        verbose_name=_('Severity')
    )

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_('IP Address')
    )

    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('User Agent')
    )

    metadata = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('Metadata')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Recorded At')
    )

    class Meta:
        verbose_name = _('System Audit Log')
        verbose_name_plural = _('System Audit Logs')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} on {self.model_name} at {self.created_at}"


class FAQ(models.Model):
    """
    Model for Frequently Asked Questions.
    """
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('orders', 'Orders & Cart'),
        ('delivery', 'Delivery & Tracking'),
        ('payment', 'Payments & Wallets'),
        ('account', 'Account & Profile'),
        ('technical', 'Technical Support'),
    ]

    question = models.CharField(
        max_length=500,
        verbose_name=_('Question')
    )

    answer = models.TextField(
        verbose_name=_('Answer')
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        verbose_name=_('Category')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Sort Order')
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
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        ordering = ['order', 'question']

    def __str__(self):
        return self.question

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from orders.models import Order, ProductService

User = get_user_model()


class Review(models.Model):
    """
    Model for verified customer reviews and ratings.
    """
    RATING_CHOICES = [
        (1, '1 Star ★☆☆☆☆'),
        (2, '2 Stars ★★☆☆☆'),
        (3, '3 Stars ★★★☆☆'),
        (4, '4 Stars ★★★★☆'),
        (5, '5 Stars ★★★★★'),
    ]

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        limit_choices_to={'user_type': 'customer'},
        verbose_name=_('Customer')
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Order')
    )

    product = models.ForeignKey(
        ProductService,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Product / Service')
    )

    rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
        verbose_name=_('Rating')
    )

    title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Headline')
    )

    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Review Comment')
    )

    is_verified = models.BooleanField(
        default=True,
        verbose_name=_('Verified Purchase')
    )

    is_public = models.BooleanField(
        default=True,
        verbose_name=_('Visible Publicly')
    )

    helpful_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Helpful Votes')
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
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']
        unique_together = ['customer', 'order', 'product']

    def __str__(self):
        name = self.customer.get_full_name() or self.customer.username
        return f"{name} on {self.product.name} ({self.rating}★)"

    @property
    def stars(self):
        return '★' * self.rating + '☆' * (5 - self.rating)


class ReviewImage(models.Model):
    """
    Customer photo uploads attached to reviews.
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Review')
    )

    image = models.ImageField(
        upload_to='review_images/',
        verbose_name=_('Image')
    )

    caption = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Caption')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Uploaded At')
    )

    class Meta:
        verbose_name = _('Review Image')
        verbose_name_plural = _('Review Images')

    def __str__(self):
        return f"{self.review} - Image #{self.id}"


class ReviewHelpful(models.Model):
    """
    Helpful vote counter for community reviews.
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='helpful_votes',
        verbose_name=_('Review')
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='helpful_votes',
        verbose_name=_('User')
    )

    is_helpful = models.BooleanField(
        default=True,
        verbose_name=_('Is Helpful')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )

    class Meta:
        verbose_name = _('Review Helpful Vote')
        verbose_name_plural = _('Review Helpful Votes')
        unique_together = ['review', 'user']

    def __str__(self):
        name = self.user.get_full_name() or self.user.username
        return f"{name} - {self.review} - {'Helpful' if self.is_helpful else 'Unhelpful'}"


class ReviewResponse(models.Model):
    """
    Merchant / admin responses to customer reviews.
    """
    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name='response',
        verbose_name=_('Review')
    )

    responder = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_responses',
        verbose_name=_('Responder')
    )

    response = models.TextField(
        verbose_name=_('Official Response')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Replied At')
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    class Meta:
        verbose_name = _('Review Response')
        verbose_name_plural = _('Review Responses')

    def __str__(self):
        return f"Response to review #{self.review.id}"


class ReviewReport(models.Model):
    """
    Moderation reports for spam or inappropriate reviews.
    """
    REPORT_REASON_CHOICES = [
        ('spam', 'Spam or Advertising'),
        ('inappropriate', 'Inappropriate Language'),
        ('fake', 'Fraudulent or Fake'),
        ('offensive', 'Offensive Content'),
        ('other', 'Other Reason'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Moderation'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Action Taken'),
        ('dismissed', 'Dismissed'),
    ]

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name=_('Review')
    )

    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_reports',
        verbose_name=_('Reported By')
    )

    reason = models.CharField(
        max_length=30,
        choices=REPORT_REASON_CHOICES,
        default='spam',
        verbose_name=_('Reason')
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Details')
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Reported At')
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_reports',
        verbose_name=_('Moderated By')
    )

    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Moderated At')
    )

    class Meta:
        verbose_name = _('Review Report')
        verbose_name_plural = _('Review Reports')
        ordering = ['-created_at']

    def __str__(self):
        return f"Report #{self.id} on Review #{self.review.id} ({self.get_status_display()})"

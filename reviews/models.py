from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from orders.models import Order, ProductService

User = get_user_model()


class Review(models.Model):
    """
    Model for customer reviews and ratings
    """
    RATING_CHOICES = [
        (1, '১ ⭐'),
        (2, '২ ⭐⭐'),
        (3, '৩ ⭐⭐⭐'),
        (4, '৪ ⭐⭐⭐⭐'),
        (5, '৫ ⭐⭐⭐⭐⭐'),
    ]
    
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        limit_choices_to={'user_type': 'customer'},
        verbose_name=_('গ্রাহক')
    )
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('অর্ডার')
    )
    
    product = models.ForeignKey(
        ProductService,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('পণ্য/সেবা')
    )
    
    rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('রেটিং')
    )
    
    title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('শিরোনাম')
    )
    
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('মন্তব্য')
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('যাচাইকৃত')
    )
    
    is_public = models.BooleanField(
        default=True,
        verbose_name=_('পাবলিক')
    )
    
    helpful_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('সহায়ক ভোট')
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
        verbose_name = _('রিভিউ')
        verbose_name_plural = _('রিভিউ')
        ordering = ['-created_at']
        unique_together = ['customer', 'order', 'product']
    
    def __str__(self):
        return f"{self.customer.get_full_name()} - {self.product.name} - {self.rating}⭐"
    
    @property
    def stars(self):
        return '⭐' * self.rating


class ReviewImage(models.Model):
    """
    Model for review images
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('রিভিউ')
    )
    
    image = models.ImageField(
        upload_to='review_images/',
        verbose_name=_('ছবি')
    )
    
    caption = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('ক্যাপশন')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('তৈরি হয়েছে')
    )
    
    class Meta:
        verbose_name = _('রিভিউ ছবি')
        verbose_name_plural = _('রিভিউ ছবি')
    
    def __str__(self):
        return f"{self.review} - ছবি #{self.id}"


class ReviewHelpful(models.Model):
    """
    Model for tracking helpful votes on reviews
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='helpful_votes',
        verbose_name=_('রিভিউ')
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='helpful_votes',
        verbose_name=_('ব্যবহারকারী')
    )
    
    is_helpful = models.BooleanField(
        verbose_name=_('সহায়ক')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('তৈরি হয়েছে')
    )
    
    class Meta:
        verbose_name = _('রিভিউ সহায়ক ভোট')
        verbose_name_plural = _('রিভিউ সহায়ক ভোট')
        unique_together = ['review', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.review} - {'সহায়ক' if self.is_helpful else 'অসহায়ক'}"


class ReviewResponse(models.Model):
    """
    Model for admin/merchant responses to reviews
    """
    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name='response',
        verbose_name=_('রিভিউ')
    )
    
    responder = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_responses',
        verbose_name=_('উত্তরদাতা')
    )
    
    response = models.TextField(
        verbose_name=_('উত্তর')
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
        verbose_name = _('রিভিউ উত্তর')
        verbose_name_plural = _('রিভিউ উত্তর')
    
    def __str__(self):
        return f"{self.review} - উত্তর"


class ReviewReport(models.Model):
    """
    Model for reporting inappropriate reviews
    """
    REPORT_REASON_CHOICES = [
        ('spam', 'স্প্যাম'),
        ('inappropriate', 'অনুপযুক্ত'),
        ('fake', 'জাল'),
        ('offensive', 'আপত্তিকর'),
        ('other', 'অন্যান্য'),
    ]
    
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name=_('রিভিউ')
    )
    
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_reports',
        verbose_name=_('রিপোর্টার')
    )
    
    reason = models.CharField(
        max_length=20,
        choices=REPORT_REASON_CHOICES,
        verbose_name=_('কারণ')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('বিবরণ')
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'অপেক্ষমান'),
            ('reviewed', 'পর্যালোচিত'),
            ('resolved', 'সমাধান'),
            ('dismissed', 'খারিজ'),
        ],
        default='pending',
        verbose_name=_('অবস্থা')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('তৈরি হয়েছে')
    )
    
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_reports',
        verbose_name=_('পর্যালোচনা করেছেন')
    )
    
    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('পর্যালোচনা হয়েছে')
    )
    
    class Meta:
        verbose_name = _('রিভিউ রিপোর্ট')
        verbose_name_plural = _('রিভিউ রিপোর্ট')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.review} - {self.get_reason_display()}"
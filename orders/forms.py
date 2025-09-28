from django import forms
from django.contrib.auth import get_user_model
from .models import Order, OrderItem, ProductService

User = get_user_model()


class OrderForm(forms.ModelForm):
    """
    Order form
    """
    class Meta:
        model = Order
        fields = [
            'delivery_type', 'scheduled_delivery_time', 'delivery_address', 
            'delivery_city', 'delivery_instructions', 'special_instructions'
        ]
        widgets = {
            'delivery_type': forms.Select(attrs={'class': 'form-control'}),
            'scheduled_delivery_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'আপনার সম্পূর্ণ ঠিকানা লিখুন'
            }),
            'delivery_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'শহরের নাম'
            }),
            'delivery_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ডেলিভারি সম্পর্কে বিশেষ নির্দেশনা (যদি থাকে)'
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'অর্ডার সম্পর্কে বিশেষ নির্দেশনা (যদি থাকে)'
            }),
        }
        labels = {
            'delivery_type': 'ডেলিভারি ধরন',
            'scheduled_delivery_time': 'নির্ধারিত ডেলিভারি সময়',
            'delivery_address': 'ডেলিভারি ঠিকানা',
            'delivery_city': 'শহর',
            'delivery_instructions': 'ডেলিভারি নির্দেশনা',
            'special_instructions': 'বিশেষ নির্দেশনা',
        }


class OrderItemForm(forms.ModelForm):
    """
    Order item form
    """
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
        }
        labels = {
            'product': 'পণ্য/সেবা',
            'quantity': 'পরিমাণ',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = ProductService.objects.filter(is_available=True)
    
    def save(self, commit=True):
        order_item = super().save(commit=False)
        if commit:
            order_item.unit_price = order_item.product.price
            order_item.save()
        return order_item


class OrderSearchForm(forms.Form):
    """
    Order search form
    """
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'অর্ডার নম্বর বা পণ্যের নাম দিয়ে খুঁজুন'
        }),
        label='খুঁজুন'
    )
    
    status = forms.ChoiceField(
        choices=[('', 'সব অবস্থা')] + Order.ORDER_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='অবস্থা'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='শুরুর তারিখ'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='শেষ তারিখ'
    )


class ProductSearchForm(forms.Form):
    """
    Product search form
    """
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'পণ্যের নাম বা বিবরণ দিয়ে খুঁজুন'
        }),
        label='খুঁজুন'
    )
    
    category = forms.ChoiceField(
        choices=[('', 'সব বিভাগ')] + ProductService.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='বিভাগ'
    )
    
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'ন্যূনতম দাম',
            'min': '0',
            'step': '0.01'
        }),
        label='ন্যূনতম দাম (৳)'
    )
    
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'সর্বোচ্চ দাম',
            'min': '0',
            'step': '0.01'
        }),
        label='সর্বোচ্চ দাম (৳)'
    )


class OrderCancellationForm(forms.Form):
    """
    Order cancellation form with reasons and instructions
    """
    CANCELLATION_REASONS = [
        ('', 'বাতিলের কারণ নির্বাচন করুন'),
        ('changed_mind', 'মনের পরিবর্তন হয়েছে'),
        ('wrong_order', 'ভুল অর্ডার দেওয়া হয়েছে'),
        ('delivery_issue', 'ডেলিভারি সমস্যা'),
        ('price_issue', 'দাম বেশি মনে হচ্ছে'),
        ('found_elsewhere', 'অন্য জায়গায় পেয়ে গেছি'),
        ('no_longer_needed', 'আর প্রয়োজন নেই'),
        ('payment_issue', 'পেমেন্ট সমস্যা'),
        ('delivery_time_issue', 'ডেলিভারি সময় সমস্যা'),
        ('product_quality_concern', 'পণ্যের মান নিয়ে উদ্বেগ'),
        ('other', 'অন্যান্য'),
    ]
    
    reason = forms.ChoiceField(
        choices=CANCELLATION_REASONS,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label='বাতিলের কারণ',
        help_text='অর্ডার বাতিল করার কারণ নির্বাচন করুন'
    )
    
    additional_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'আপনার বাতিলের কারণ সম্পর্কে বিস্তারিত জানান (ঐচ্ছিক)',
            'maxlength': '500'
        }),
        required=False,
        label='অতিরিক্ত নোট',
        help_text='আপনার মতামত আমাদের উন্নতিতে সাহায্য করবে'
    )
    
    confirm_cancellation = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'required': True
        }),
        label='আমি নিশ্চিত যে আমি এই অর্ডার বাতিল করতে চাই',
        help_text='এই চেকবক্সটি চেক করে আপনি নিশ্চিত করুন যে আপনি অর্ডার বাতিল করতে চান'
    )
    
    refund_preference = forms.ChoiceField(
        choices=[
            ('', 'রিফান্ড পছন্দ নির্বাচন করুন'),
            ('refund_to_payment_method', 'মূল পেমেন্ট পদ্ধতিতে রিফান্ড'),
            ('refund_to_wallet', 'ওয়ালেটে রিফান্ড'),
            ('no_refund_needed', 'রিফান্ড প্রয়োজন নেই'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        required=False,
        label='রিফান্ড পছন্দ',
        help_text='আপনি কিভাবে রিফান্ড পেতে চান?'
    )
    
    def clean_confirm_cancellation(self):
        confirmed = self.cleaned_data.get('confirm_cancellation')
        if not confirmed:
            raise forms.ValidationError('অর্ডার বাতিল করতে হলে আপনাকে নিশ্চিত করতে হবে।')
        return confirmed
    
    def clean_reason(self):
        reason = self.cleaned_data.get('reason')
        if not reason:
            raise forms.ValidationError('বাতিলের কারণ নির্বাচন করা বাধ্যতামূলক।')
        return reason
from django import forms
from django.contrib.auth import get_user_model
from .models import Order, OrderItem, ProductService

User = get_user_model()


class OrderForm(forms.ModelForm):
    """
    Form for editing or creating delivery order details.
    """
    class Meta:
        model = Order
        fields = [
            'delivery_type',
            'scheduled_delivery_time',
            'delivery_address',
            'delivery_city',
            'delivery_instructions',
            'special_instructions',
        ]
        widgets = {
            'delivery_type': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_delivery_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Full street address, apartment/floor details'
            }),
            'delivery_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Area / Zone name'
            }),
            'delivery_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Special delivery access instructions (optional)'
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Order packaging instructions (optional)'
            }),
        }
        labels = {
            'delivery_type': 'Delivery Option',
            'scheduled_delivery_time': 'Preferred Delivery Time',
            'delivery_address': 'Delivery Address',
            'delivery_city': 'Area / Zone',
            'delivery_instructions': 'Delivery Instructions',
            'special_instructions': 'Special Notes',
        }


class OrderItemForm(forms.ModelForm):
    """
    Form to manage items inside an order.
    """
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
        }
        labels = {
            'product': 'Product / Item',
            'quantity': 'Quantity',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = ProductService.objects.filter(is_available=True)

    def save(self, commit=True):
        order_item = super().save(commit=False)
        order_item.unit_price = order_item.product.price
        order_item.total_price = order_item.unit_price * order_item.quantity
        if commit:
            order_item.save()
        return order_item


class OrderSearchForm(forms.Form):
    """
    Admin and customer order filter form.
    """
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by order reference or customer...'
        }),
        label='Search'
    )

    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Order.ORDER_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Status'
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='From Date'
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='To Date'
    )


class ProductSearchForm(forms.Form):
    """
    Search and filter form for products.
    """
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search essentials, food, groceries...'
        }),
        label='Search'
    )

    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + ProductService.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Category'
    )

    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min (৳)',
            'min': '0',
            'step': '1'
        }),
        label='Min Price (৳)'
    )

    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max (৳)',
            'min': '0',
            'step': '1'
        }),
        label='Max Price (৳)'
    )


class OrderCancellationForm(forms.Form):
    """
    Order cancellation form with validation.
    """
    CANCELLATION_REASONS = [
        ('', 'Select cancellation reason...'),
        ('changed_mind', 'Changed my mind'),
        ('wrong_items', 'Ordered incorrect items'),
        ('delivery_delay', 'Delivery turnaround too long'),
        ('found_cheaper', 'Found a better price elsewhere'),
        ('accidental_order', 'Placed order by mistake'),
        ('payment_issue', 'Payment method issues'),
        ('other', 'Other reason'),
    ]

    reason = forms.ChoiceField(
        choices=CANCELLATION_REASONS,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        label='Reason for Cancellation',
        help_text='Please tell us why you are cancelling this order'
    )

    additional_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional context or feedback (optional)',
            'maxlength': '500'
        }),
        required=False,
        label='Additional Notes'
    )

    confirm_cancellation = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'required': True
        }),
        label='I confirm that I want to cancel this order',
        help_text='Cancellation is permanent and cannot be reversed.'
    )

    refund_preference = forms.ChoiceField(
        choices=[
            ('', 'Select refund preference...'),
            ('original_method', 'Refund to original payment channel'),
            ('swift_wallet', 'Credit to SwiftDrop wallet balance'),
            ('no_refund', 'No refund required (e.g. COD unpaid)'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False,
        label='Refund Preference',
        help_text='How would you like eligible refunds to be processed?'
    )

    def clean_confirm_cancellation(self):
        confirmed = self.cleaned_data.get('confirm_cancellation')
        if not confirmed:
            raise forms.ValidationError('You must check the confirmation box to cancel your order.')
        return confirmed

    def clean_reason(self):
        reason = self.cleaned_data.get('reason')
        if not reason:
            raise forms.ValidationError('Please choose a reason for cancelling.')
        return reason

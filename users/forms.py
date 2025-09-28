from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from .models import CustomerProfile, DeliveryAgentProfile

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form with Bengali support
    """
    email = forms.EmailField(
        label='ইমেইল',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'আপনার ইমেইল ঠিকানা'
        })
    )
    
    first_name = forms.CharField(
        label='নাম',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'আপনার নাম'
        })
    )
    
    last_name = forms.CharField(
        label='উপাধি',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'আপনার উপাধি'
        })
    )
    
    phone_number = forms.CharField(
        label='ফোন নম্বর',
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '০১XXXXXXXXX'
        })
    )
    
    user_type = forms.ChoiceField(
        label='ব্যবহারকারীর ধরন',
        choices=User.USER_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='customer'
    )
    
    address = forms.CharField(
        label='ঠিকানা',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'আপনার সম্পূর্ণ ঠিকানা'
        }),
        required=False
    )
    
    city = forms.CharField(
        label='শহর',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'আপনার শহর'
        }),
        required=False
    )
    
    postal_code = forms.CharField(
        label='পোস্টাল কোড',
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'পোস্টাল কোড'
        }),
        required=False
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'user_type', 'address', 'city', 'postal_code', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'ব্যবহারকারী নাম'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'পাসওয়ার্ড'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'পাসওয়ার্ড নিশ্চিত করুন'})
        
        # Add labels
        self.fields['username'].label = 'ব্যবহারকারী নাম'
        self.fields['password1'].label = 'পাসওয়ার্ড'
        self.fields['password2'].label = 'পাসওয়ার্ড নিশ্চিত করুন'
        
        # Set initial values for required fields
        if not self.instance.pk:  # Only for new users
            self.fields['user_type'].initial = 'customer'
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('এই ফোন নম্বর দিয়ে ইতিমধ্যে একটি অ্যাকাউন্ট রয়েছে।')
        return phone_number
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = self.cleaned_data.get('user_type', 'customer')
        if commit:
            user.save()
            # Create customer profile if user is customer
            if user.user_type == 'customer':
                CustomerProfile.objects.get_or_create(user=user)
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form with Bengali support
    """
    username = forms.CharField(
        label='ব্যবহারকারী নাম',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ব্যবহারকারী নাম বা ইমেইল'
        })
    )
    
    password = forms.CharField(
        label='পাসওয়ার্ড',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'পাসওয়ার্ড'
        })
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Custom password change form with Bengali support
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})
        
        self.fields['old_password'].label = 'পুরাতন পাসওয়ার্ড'
        self.fields['new_password1'].label = 'নতুন পাসওয়ার্ড'
        self.fields['new_password2'].label = 'নতুন পাসওয়ার্ড নিশ্চিত করুন'


class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom password reset form with Bengali support
    """
    email = forms.EmailField(
        label='ইমেইল',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'আপনার ইমেইল ঠিকানা'
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    """
    Custom set password form with Bengali support
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})
        
        self.fields['new_password1'].label = 'নতুন পাসওয়ার্ড'
        self.fields['new_password2'].label = 'নতুন পাসওয়ার্ড নিশ্চিত করুন'


class UserProfileForm(forms.ModelForm):
    """
    User profile form
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'address', 'city', 'postal_code', 'profile_picture')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'নাম',
            'last_name': 'উপাধি',
            'email': 'ইমেইল',
            'phone_number': 'ফোন নম্বর',
            'address': 'ঠিকানা',
            'city': 'শহর',
            'postal_code': 'পোস্টাল কোড',
            'profile_picture': 'প্রোফাইল ছবি',
        }


class CustomerProfileForm(forms.ModelForm):
    """
    Customer profile form
    """
    class Meta:
        model = CustomerProfile
        fields = ('preferred_language', 'emergency_contact', 'delivery_instructions')
        widgets = {
            'preferred_language': forms.Select(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'preferred_language': 'পছন্দের ভাষা',
            'emergency_contact': 'জরুরি যোগাযোগ',
            'delivery_instructions': 'ডেলিভারি নির্দেশনা',
        }


class DeliveryAgentProfileForm(forms.ModelForm):
    """
    Delivery agent profile form
    """
    class Meta:
        model = DeliveryAgentProfile
        fields = ('license_number', 'vehicle_type', 'vehicle_number')
        widgets = {
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-control'}),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'license_number': 'লাইসেন্স নম্বর',
            'vehicle_type': 'যানবাহনের ধরন',
            'vehicle_number': 'যানবাহনের নম্বর',
        }


class DeliveryAgentSignupForm(CustomUserCreationForm):
    """
    Delivery agent signup form
    """
    license_number = forms.CharField(
        label='লাইসেন্স নম্বর',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'আপনার লাইসেন্স নম্বর'
        })
    )
    
    vehicle_type = forms.ChoiceField(
        label='যানবাহনের ধরন',
        choices=DeliveryAgentProfile._meta.get_field('vehicle_type').choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    vehicle_number = forms.CharField(
        label='যানবাহনের নম্বর',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'যানবাহনের নম্বর'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_type'].initial = 'delivery_agent'
        self.fields['user_type'].widget = forms.HiddenInput()
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'delivery_agent'
        if commit:
            user.save()
            DeliveryAgentProfile.objects.create(
                user=user,
                license_number=self.cleaned_data['license_number'],
                vehicle_type=self.cleaned_data['vehicle_type'],
                vehicle_number=self.cleaned_data['vehicle_number']
            )
        return user

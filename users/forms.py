from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth import get_user_model
from .models import CustomerProfile, DeliveryAgentProfile

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    User registration form with email, phone, and address support.
    """
    first_name = forms.CharField(
        label='First Name',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )

    last_name = forms.CharField(
        label='Last Name',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )

    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com'
        })
    )

    phone_number = forms.CharField(
        label='Phone Number',
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+8801XXXXXXXXX'
        })
    )

    user_type = forms.ChoiceField(
        label='Account Type',
        choices=User.USER_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='customer'
    )

    address = forms.CharField(
        label='Street Address',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'House, road, apartment...'
        }),
        required=False
    )

    city = forms.CharField(
        label='City / Area',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Dhaka'
        }),
        required=False
    )

    postal_code = forms.CharField(
        label='Postal Code',
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. 1205'
        }),
        required=False
    )

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'user_type',
            'address',
            'city',
            'postal_code',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a unique username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })

        self.fields['username'].label = 'Username'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'

        if not self.instance.pk:
            self.fields['user_type'].initial = 'customer'

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and User.objects.filter(phone_number=phone_number).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('An account with this phone number already exists.')
        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('An account with this email address already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = self.cleaned_data.get('user_type', 'customer')
        if commit:
            user.save()
            if user.user_type == 'customer':
                CustomerProfile.objects.get_or_create(user=user)
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Authentication form supporting email or username login.
    """
    username = forms.CharField(
        label='Email or Username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com or username',
            'autofocus': True,
        })
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
        })
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Current password'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'New password'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm new password'})
        self.fields['old_password'].label = 'Current Password'
        self.fields['new_password1'].label = 'New Password'
        self.fields['new_password2'].label = 'Confirm New Password'


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email'
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'New password'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm new password'})
        self.fields['new_password1'].label = 'New Password'
        self.fields['new_password2'].label = 'Confirm New Password'


class UserProfileForm(forms.ModelForm):
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
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'address': 'Delivery Address',
            'city': 'City / Area',
            'postal_code': 'Postal Code',
            'profile_picture': 'Profile Picture',
        }


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ('preferred_language', 'emergency_contact', 'delivery_instructions')
        widgets = {
            'preferred_language': forms.Select(attrs={'class': 'form-select'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency contact phone'}),
            'delivery_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'e.g. Ring bell or call on arrival'}),
        }
        labels = {
            'preferred_language': 'Preferred Language',
            'emergency_contact': 'Emergency Contact',
            'delivery_instructions': 'Delivery Instructions',
        }


class DeliveryAgentProfileForm(forms.ModelForm):
    class Meta:
        model = DeliveryAgentProfile
        fields = ('license_number', 'vehicle_type', 'vehicle_number', 'is_available')
        widgets = {
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'license_number': 'Driver License Number',
            'vehicle_type': 'Vehicle Type',
            'vehicle_number': 'Vehicle Plate Number',
            'is_available': 'Available for Deliveries',
        }


class DeliveryAgentSignupForm(CustomUserCreationForm):
    license_number = forms.CharField(
        label='Driving License Number',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Driving license number'
        })
    )

    vehicle_type = forms.ChoiceField(
        label='Vehicle Type',
        choices=DeliveryAgentProfile._meta.get_field('vehicle_type').choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    vehicle_number = forms.CharField(
        label='Vehicle Plate Number',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Plate number (e.g. DHK-MET-1234)'
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

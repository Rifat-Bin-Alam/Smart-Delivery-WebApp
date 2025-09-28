from django import forms
from .models import Review, ReviewImage, ReviewReport

class ReviewForm(forms.ModelForm):
    """
    Review form
    """
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'রিভিউের শিরোনাম (যদি থাকে)'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'আপনার মতামত লিখুন'
            }),
        }
        labels = {
            'rating': 'রেটিং',
            'title': 'শিরোনাম',
            'comment': 'মন্তব্য',
        }


class ReviewImageForm(forms.ModelForm):
    """
    Review image form
    """
    class Meta:
        model = ReviewImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ছবির ক্যাপশন (যদি থাকে)'
            }),
        }
        labels = {
            'image': 'ছবি',
            'caption': 'ক্যাপশন',
        }


class ReviewReportForm(forms.ModelForm):
    """
    Review report form
    """
    class Meta:
        model = ReviewReport
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'রিপোর্টের কারণ বিস্তারিত লিখুন'
            }),
        }
        labels = {
            'reason': 'কারণ',
            'description': 'বিবরণ',
        }

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
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review headline (e.g., Fast delivery & fresh items)'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Share your experience with this essential and the delivery service...'
            }),
        }
        labels = {
            'rating': 'Rating',
            'title': 'Review Headline',
            'comment': 'Detailed Feedback',
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
                'placeholder': 'Photo caption (optional)'
            }),
        }
        labels = {
            'image': 'Photo',
            'caption': 'Caption',
        }


class ReviewReportForm(forms.ModelForm):
    """
    Review report form
    """
    class Meta:
        model = ReviewReport
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please describe why this review violates platform policies...'
            }),
        }
        labels = {
            'reason': 'Reason for Report',
            'description': 'Details',
        }

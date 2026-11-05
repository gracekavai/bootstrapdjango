from django import forms

from myapp.models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'subject', 'message')
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your Name...',
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Your E-mail...',
                'autocomplete': 'email',
            }),
            'subject': forms.TextInput(attrs={'placeholder': 'Subject...'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your Message'}),
        }
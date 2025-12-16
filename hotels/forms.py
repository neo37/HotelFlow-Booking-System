from django import forms
from .models import Booking
from datetime import date


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['guest_name', 'guest_email', 'guest_phone', 'check_in', 'check_out']
        widgets = {
            'guest_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'guest_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
            'guest_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 123-45-67'}),
            'check_in': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'check_out': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'guest_name': 'Имя',
            'guest_email': 'Email',
            'guest_phone': 'Телефон',
            'check_in': 'Дата заезда',
            'check_out': 'Дата выезда',
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')

        if check_in and check_out:
            if check_in < date.today():
                raise forms.ValidationError('Дата заезда не может быть в прошлом.')
            if check_out <= check_in:
                raise forms.ValidationError('Дата выезда должна быть позже даты заезда.')

        return cleaned_data


class DateFilterForm(forms.Form):
    check_in = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Дата заезда'
    )
    check_out = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Дата выезда'
    )



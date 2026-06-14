from django import forms


class CheckoutForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
               attrs={'class': 'form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
               attrs={'class': 'form-control', 'placeholder': 'Last name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
               attrs={'class': 'form-control', 'placeholder': 'Email address'})
    )
    phone = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(
                attrs={'class': 'form-control',
                       'placeholder': 'Phone number (optional)'})
    )
    street = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
               attrs={'class': 'form-control', 'placeholder': 'Street name'})
    )
    building = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(
               attrs={'class': 'form-control',
                      'placeholder': 'Building/apartment number'})
    )
    postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
               attrs={'class': 'form-control', 'placeholder': 'Postal code'})
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
               attrs={'class': 'form-control', 'placeholder': 'City'})
    )
    country = forms.CharField(
        max_length=100, initial='Sweden',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
               attrs={'class': 'form-control',
                      'rows': 3, 'placeholder': 'Order notes (optional)'})
    )

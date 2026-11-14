from django import forms
from .models import Order


class CheckoutForm(forms.Form):
    # Address selection
    selected_address_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    # New address fields if user enters a new one
    use_new_address = forms.BooleanField(required=False, widget=forms.HiddenInput())
    full_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile number'}))
    street_address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Flat / House no. / Street'}))
    landmark = forms.CharField(max_length=120, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Landmark (Optional)'}))
    city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}))
    state = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}))
    postal_code = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PIN code'}))
    address_type = forms.ChoiceField(choices=[('HOME', 'Home'), ('WORK', 'Work')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))

    # Payment selection
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHODS,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    # Simulated payment details
    upi_id = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'username@okhdfcbank or phone@upi'}))
    card_number = forms.CharField(max_length=19, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '4532 •••• •••• 8912'}))
    card_holder = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name on Card'}))
    card_expiry = forms.CharField(max_length=5, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY'}))
    card_cvv = forms.CharField(max_length=4, required=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'CVV'}))
    bank_name = forms.CharField(max_length=50, required=False, widget=forms.Select(
        choices=[
            ('', '-- Choose Bank --'),
            ('HDFC', 'HDFC Bank'),
            ('ICICI', 'ICICI Bank'),
            ('SBI', 'State Bank of India'),
            ('AXIS', 'Axis Bank'),
            ('KOTAK', 'Kotak Mahindra Bank'),
        ],
        attrs={'class': 'form-select'}
    ))

    # Coupon
    coupon_code = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Promo Code'}))

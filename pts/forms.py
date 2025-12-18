from django import forms
from .models import Drug, Transaction
from datetime import date

class DrugForm(forms.ModelForm):
    class Meta:
        model = Drug
        fields = '__all__'
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_expiry_date(self):
        expiry = self.cleaned_data.get('expiry_date')
        if expiry < date.today():
            raise forms.ValidationError("Expiry date must be in the future.")
        return expiry

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['drug', 'type', 'quantity']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be positive.")
        return quantity
    
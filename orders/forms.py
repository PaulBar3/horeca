from django import forms

from .models import Order

INPUT_CLASS = "w-full fc-input border rounded px-3 py-2 text-sm"


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["contact_name", "company", "phone", "email", "comment"]
        widgets = {
            "contact_name": forms.TextInput(attrs={
                "placeholder": "ФИО *",
                "class": INPUT_CLASS,
            }),
            "company": forms.TextInput(attrs={
                "placeholder": "Компания",
                "class": INPUT_CLASS,
            }),
            "phone": forms.TextInput(attrs={
                "placeholder": "Телефон *",
                "class": INPUT_CLASS,
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Email *",
                "class": INPUT_CLASS,
            }),
            "comment": forms.Textarea(attrs={
                "placeholder": "Комментарий",
                "rows": 2,
                "class": INPUT_CLASS,
            }),
        }

from django import forms

from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["contact_name", "company", "phone", "email", "comment"]
        widgets = {
            "contact_name": forms.TextInput(attrs={
                "placeholder": "ФИО *",
                "class": "border rounded px-3 py-2 text-sm",
            }),
            "company": forms.TextInput(attrs={
                "placeholder": "Компания",
                "class": "border rounded px-3 py-2 text-sm",
            }),
            "phone": forms.TextInput(attrs={
                "placeholder": "Телефон *",
                "class": "border rounded px-3 py-2 text-sm",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Email *",
                "class": "border rounded px-3 py-2 text-sm",
            }),
            "comment": forms.Textarea(attrs={
                "placeholder": "Комментарий",
                "rows": 2,
                "class": "w-full border rounded px-3 py-2 text-sm",
            }),
        }

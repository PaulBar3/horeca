from django import forms

from .models import Lead


class ContactForm(forms.ModelForm):
    message = forms.CharField(
        label="Сообщение",
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "Сообщение *",
            "class": "w-full fc-input border rounded px-3 py-2 text-sm",
        }),
    )

    class Meta:
        model = Lead
        fields = ["contact_name", "email", "phone", "message"]
        widgets = {
            "contact_name": forms.TextInput(attrs={
                "placeholder": "ФИО *",
                "class": "w-full fc-input border rounded px-3 py-2 text-sm",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Email *",
                "class": "w-full fc-input border rounded px-3 py-2 text-sm",
            }),
            "phone": forms.TextInput(attrs={
                "placeholder": "Телефон",
                "class": "w-full fc-input border rounded px-3 py-2 text-sm",
            }),
        }


class TrialRequestForm(forms.ModelForm):
    company = forms.CharField(
        label="Компания",
        widget=forms.TextInput(attrs={
            "placeholder": "Компания *",
            "class": "w-full fc-input border rounded px-3 py-2 text-sm",
        }),
    )
    phone = forms.CharField(
        label="Телефон",
        widget=forms.TextInput(attrs={
            "placeholder": "Телефон *",
            "class": "w-full fc-input border rounded px-3 py-2 text-sm",
        }),
    )
    message = forms.CharField(
        label="Комментарий",
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 2,
            "placeholder": "Комментарий",
            "class": "w-full fc-input border rounded px-3 py-2 text-sm",
        }),
    )

    class Meta:
        model = Lead
        fields = ["contact_name", "company", "phone", "email", "message"]
        widgets = {
            "contact_name": forms.TextInput(attrs={
                "placeholder": "ФИО *",
                "class": "w-full fc-input border rounded px-3 py-2 text-sm",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Email *",
                "class": "w-full fc-input border rounded px-3 py-2 text-sm",
            }),
        }

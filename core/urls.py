from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", TemplateView.as_view(template_name="core/about.html"), name="about"),
    path("b2b/", views.b2b, name="b2b"),
    path("b2b/trial-request/", views.b2b, name="trial_request"),
    path("contacts/", views.contacts, name="contacts"),
]

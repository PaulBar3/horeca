from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", TemplateView.as_view(template_name="core/about.html"), name="about"),
    path("b2b/", TemplateView.as_view(template_name="core/b2b.html"), name="b2b"),
    path("b2b/trial-request/", views.trial_request, name="trial_request"),
    path("contacts/", views.contacts, name="contacts"),
]

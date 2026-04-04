from django.urls import path
from . import views

app_name = "billing"

urlpatterns = [
    path("checkout/", views.checkout_session, name="checkout"),
    path("success/", views.payment_success, name="success"),
    path("webhook/", views.webhook, name="webhook"),
    path("invoices/", views.my_invoices, name="invoices"),
]

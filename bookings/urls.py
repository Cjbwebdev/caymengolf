from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [
    path("", views.booking_page, name="booking"),
]

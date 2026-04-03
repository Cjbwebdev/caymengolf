from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [
    path("", views.booking_page, name="booking"),
    path("slot/<int:time_id>/", views.book_slot, name="book_slot"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("my-bookings/<int:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("lesson/<int:slot_id>/", views.book_lesson, name="book_lesson"),
]

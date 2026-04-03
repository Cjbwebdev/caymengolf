from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("bookings/", views.bookings_page, name="bookings"),
    path("lessons/", views.lessons_page, name="lessons"),
]

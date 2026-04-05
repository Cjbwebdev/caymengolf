from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("bookings/", views.bookings_page, name="bookings"),
    path("lessons/", views.lessons_page, name="lessons"),
    path("leaderboard/", RedirectView.as_view(url="/golfers/leaderboard/", permanent=False)),
]

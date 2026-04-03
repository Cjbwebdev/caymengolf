from django.urls import path
from . import views

app_name = "golfers"

urlpatterns = [
    path("profile/", views.my_profile, name="my_profile"),
    path("profile/<str:username>/", views.golfer_profile, name="profile"),
    path("submit-score/", views.submit_score, name="submit_score"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("signup/", views.signup_view, name="signup"),
]

from django.shortcuts import render, redirect
from django.utils import timezone
from bookings.views import booking_page as bp, lessons_page as lp
from datetime import timedelta

def home(request):
    from golfers.models import WeeklyLeaderboard
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_best = WeeklyLeaderboard.objects.filter(week_start=week_start).order_by("score")[:5]
    return render(request, "index.html", {"week_best": week_best})

def about(request):
    return render(request, "pages/about.html")

def bookings_page(request):
    return bp(request)

def lessons_page(request):
    return lp(request)

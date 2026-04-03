from django.shortcuts import render
from django.utils import timezone
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
    from bookings.models import TeeTime
    date_str = request.GET.get("date", str(timezone.now().date()))
    times = TeeTime.objects.filter(date=date_str, is_available=True).order_by("time")
    return render(request, "pages/bookings.html", {"tee_times": times, "selected_date": date_str})

def lessons_page(request):
    from lessons.models import LessonType
    types = LessonType.objects.filter(is_active=True)
    return render(request, "pages/lessons.html", {"lesson_types": types})

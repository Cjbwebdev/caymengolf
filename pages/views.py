from django.shortcuts import render, redirect
from django.views.generic import RedirectView
from django.utils import timezone
from datetime import timedelta
from bookings.views import booking_page as bp, lessons_page as lp
from golfers.models import WeeklyLeaderboard, Score


def home(request):
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())

    # Try WeeklyLeaderboard first
    week_best = list(
        WeeklyLeaderboard.objects.select_related("golfer__user")
        .filter(week_start=week_start)
        .order_by("score")[:5]
    )

    # Fallback: scores this week if no leaderboard entries exist
    if not week_best:
        week_scores = Score.objects.select_related("golfer__user").filter(
            date__gte=week_start
        ).order_by("total_score")
        seen = set()
        for s in week_scores[:20]:
            if s.golfer_id not in seen:
                seen.add(s.golfer_id)
                week_best.append(s)
        week_best = week_best[:5]

    return render(request, "index.html", {"week_best": week_best})


def about(request):
    return render(request, "pages/about.html")


def bookings_page(request):
    return bp(request)


def lessons_page(request):
    return lp(request)

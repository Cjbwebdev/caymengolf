from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import GolferProfile, Score, WeeklyLeaderboard

def golfer_profile(request, username):
    profile = get_object_or_404(GolferProfile, user__username=username)
    if not profile.is_public and request.user != profile.user:
        messages.error(request, "This profile is private.")
        return redirect("pages:home")
    context = {
        "profile": profile,
        "recent_scores": profile.recent_scores[:10],
        "best_round": profile.best_round,
        "rounds_played": profile.rounds_played,
        "average_score": profile.average_score,
        "handicap_progress": profile.handicap_progress,
    }
    return render(request, "golfers/profile.html", context)

@login_required
def my_profile(request):
    return golfer_profile(request, request.user.username)

@login_required
def submit_score(request):
    if request.method == "POST":
        total_score = int(request.POST.get("total_score", 0))
        par = int(request.POST.get("par", 71))
        date_str = request.POST.get("date", str(timezone.now().date()))
        front_9 = request.POST.get("front_9")
        back_9 = request.POST.get("back_9")
        profile = request.user.golf_profile
        Score.objects.create(
            golfer=profile, date=date_str, total_score=total_score, par=par,
            front_9=int(front_9) if front_9 else None,
            back_9=int(back_9) if back_9 else None,
            handicap_at_time=profile.handicap_index,
        )
        new_handicap = profile.calculate_handicap()
        if new_handicap is not None:
            profile.handicap_index = new_handicap
            profile.save()
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        WeeklyLeaderboard.objects.update_or_create(
            golfer=profile, week_start=week_start,
            defaults={"score": total_score, "week_end": week_end},
        )
        messages.success(request, f"Score {total_score} submitted!")
        return redirect("golfers:my_profile")
    return render(request, "golfers/submit_score.html")

def leaderboard(request):
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_best = WeeklyLeaderboard.objects.filter(week_start=week_start).order_by("score")[:10]
    all_time_best = Score.objects.order_by("total_score")[:10]
    return render(request, "golfers/leaderboard.html", {"week_best": week_best, "all_time_best": all_time_best, "week_start": week_start})

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            GolferProfile.objects.create(user=user, display_name=user.username)
            auth_login(request, user)
            messages.success(request, "Welcome to Cayman Golf!")
            return redirect("pages:home")
    else:
        form = UserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from datetime import timedelta
from golfers.models import GolferProfile, Score, DEFAULT_PAR, WeeklyLeaderboard


@login_required
def submit_score(request):
    profile, _ = GolferProfile.objects.get_or_create(user=request.user)
    today = timezone.now().date()

    if request.method == "POST":
        hole_scores = {}
        total = 0
        for hole in range(1, 19):
            val = request.POST.get(f"hole_{hole}", "").strip()
            if val:
                try:
                    score_val = int(val)
                    hole_scores[str(hole)] = score_val
                    total += score_val
                except ValueError:
                    pass
        
        if len(hole_scores) < 18:
            messages.error(request, f"Please enter scores for all 18 holes. Entered: {len(hole_scores)}/18")
            return render(request, "golfers/submit_score.html", {
                "par": DEFAULT_PAR,
                "profile": profile,
                "today": today,
                "existing": {},
            })
        
        front_9 = sum(hole_scores.get(str(h), 0) for h in range(1, 10))
        back_9 = sum(hole_scores.get(str(h), 0) for h in range(10, 19))
        par_total = sum(DEFAULT_PAR)
        league = request.POST.get("league", "all")
        course_conditions = request.POST.get("course_conditions", "")
        notes = request.POST.get("notes", "")

        score = Score.objects.create(
            golfer=profile,
            date=today,
            total_score=total,
            par=par_total,
            front_9=front_9,
            back_9=back_9,
            hole_scores=hole_scores,
            league=league,
            course_conditions=course_conditions,
            notes=notes,
        )

        handicap = score.auto_calc_handicap()
        if handicap is not None:
            profile.handicap_index = handicap
            profile.save()

        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        best = Score.objects.filter(golfer=profile, date__gte=week_start, date__lte=week_end).order_by("total_score").first()
        if best:
            WeeklyLeaderboard.objects.update_or_create(
                golfer=profile,
                week_start=week_start,
                defaults={"score": best.total_score, "week_end": week_end},
            )

        par_str = "+" + str(total - par_total) if total >= par_total else str(total - par_total)
        messages.success(request, f"Score submitted! {total} ({par_str})")
        return redirect("golfers:my_profile")

    existing = {}
    return render(request, "golfers/submit_score.html", {
        "par": DEFAULT_PAR,
        "profile": profile,
        "today": today,
        "existing": existing,
    })


@login_required
def my_profile(request):
    profile, _ = GolferProfile.objects.get_or_create(user=request.user)
    scores = profile.scores.order_by("-date")[:20]
    return render(request, "golfers/profile.html", {
        "profile": profile,
        "scores": scores,
    })


def golfer_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile, _ = GolferProfile.objects.get_or_create(user=user)
    scores = profile.scores.order_by("-date")[:10]
    return render(request, "golfers/profile.html", {
        "profile": profile,
        "scores": scores,
        "viewing_other": username != request.user.username if request.user.is_authenticated else True,
    })


def leaderboard(request):
    """Leaderboard page with weekly best, all-time best, and league filters."""
    league = request.GET.get("league", "all")
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    qs = Score.objects.select_related("golfer__user").all()
    if league != "all":
        qs = qs.filter(league=league)
    
    # Weekly best: one entry per golfer
    week_qs = qs.filter(date__gte=week_start, date__lte=week_end).order_by("total_score")
    seen = {}
    for s in week_qs:
        if s.golfer_id not in seen:
            seen[s.golfer_id] = s
    week_best = sorted(seen.values(), key=lambda x: x.total_score)[:10]
    
    # All-time best: one entry per golfer
    all_qs = qs.order_by("total_score")
    seen2 = {}
    for s in all_qs:
        if s.golfer_id not in seen2:
            seen2[s.golfer_id] = s
    all_time_best = sorted(seen2.values(), key=lambda x: x.total_score)[:10]
    
    return render(request, "golfers/leaderboard.html", {
        "week_best": week_best,
        "all_time_best": all_time_best,
        "week_start": week_start,
        "week_end": week_end,
        "league": league,
    })


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("golfers:my_profile")
    
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        
        if not email or not password:
            return render(request, "golfers/signup.html", {"error": "Email and password required."})
        if password != password2:
            return render(request, "golfers/signup.html", {"error": "Passwords do not match."})
        if User.objects.filter(email=email).exists():
            return render(request, "golfers/signup.html", {"error": "Email already in use."})
        
        user = User.objects.create_user(
            username=username or email.split("@")[0],
            email=email,
            password=password
        )
        login(request, user)
        GolferProfile.objects.get_or_create(user=user)
        return redirect("golfers:my_profile")
    
    return render(request, "golfers/signup.html")

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
                    score = int(val)
                    hole_scores[str(hole)] = score
                    total += score
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

        messages.success(request, f"Score submitted! {total} ({'+' if total - par_total >= 0 else ''}{total - par_total})")
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
    """Public profile for any golfer — shows stats, best round, recent scores."""
    user = get_object_or_404(User, username=username)
    profile, _ = GolferProfile.objects.get_or_create(user=user)
    scores = profile.scores.order_by("-date")[:10]
    
    return render(request, "golfers/profile.html", {
        "profile": profile,
        "scores": scores,
        "viewing_other": username != request.user.username if request.user.is_authenticated else True,
    })


def leaderboard(request):
    league = request.GET.get("league", "all")
    scores = Score.objects.select_related("golfer").order_by("-date")
    
    if league != "all":
        scores = scores.filter(league=league)
    
    golfers = {}
    for s in scores:
        if s.golfer_id not in golfers:
            golfers[s.golfer_id] = {
                "golfer": s.golfer,
                "best": s,
                "handicap": s.golfer.handicap_index,
                "rounds": s.golfer.scores.count(),
                "avg": s.golfer.average_score,
            }
        if s.total_score < golfers[s.golfer_id]["best"].total_score:
            golfers[s.golfer_id]["best"] = s
    
    sorted_golfers = sorted(golfers.values(), key=lambda x: x["best"].total_score)
    league_label = dict(Score.LEAGUE_CHOICES).get(league, "All")
    
    return render(request, "golfers/leaderboard.html", {
        "golfers": sorted_golfers,
        "league": league,
        "league_label": league_label,
        "weekly": False,
    })


def signup_view(request):
    """Custom signup that creates both User and GolferProfile."""
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
        
        user = User.objects.create_user(username=username or email.split("@")[0], email=email, password=password)
        login(request, user)
        GolferProfile.objects.get_or_create(user=user)
        
        return redirect("golfers:my_profile")
    
    return render(request, "golfers/signup.html")

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from golfers.models import GolferProfile, Score, DEFAULT_PAR


@login_required
def submit_score(request):
    profile, _ = GolferProfile.objects.get_or_create(user=request.user)
    today = timezone.now().date()

    if request.method == "POST":
        # Collect hole-by-hole scores
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

        # Auto-update handicap
        handicap = score.auto_calc_handicap()
        if handicap is not None:
            profile.handicap_index = handicap
            profile.save()

        # Update weekly leaderboard
        from datetime import timedelta
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        from golfers.models import WeeklyLeaderboard
        best = Score.objects.filter(golfer=profile, date__gte=week_start, date__lte=week_end).order_by("total_score").first()
        if best:
            WeeklyLeaderboard.objects.update_or_create(
                golfer=profile,
                week_start=week_start,
                defaults={"score": best.total_score, "week_end": week_end},
            )

        messages.success(request, f"Score submitted! {total} ({'+' if total - par_total >= 0 else ''}{total - par_total})")
        return redirect("golfers:my_profile")

    # Pre-fill existing hole scores if editing
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


def leaderboard(request):
    league = request.GET.get("league", "all")
    scores = Score.objects.select_related("golfer").order_by("-date")
    
    if league != "all":
        scores = scores.filter(league=league)
    
    # Group by golfer and get best recent score
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
    })

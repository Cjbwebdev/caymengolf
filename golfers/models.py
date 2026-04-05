from django.db import models
from django.contrib.auth.models import User


# ── Default par values for each of the 18 holes at Cayman Golf Brixham ──
DEFAULT_PAR = [4, 3, 5, 4, 4, 3, 4, 5, 4, 4, 3, 4, 5, 4, 3, 4, 4, 4]


class GolferProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="golf_profile")
    display_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    handicap_index = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    home_course = models.CharField(max_length=200, default="Cayman Golf, Brixham")
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or self.user.username

    @property
    def best_round(self):
        best = self.scores.aggregate(low=models.Min("total_score"))["low"]
        return best

    @property
    def rounds_played(self):
        return self.scores.count()

    @property
    def average_score(self):
        avg = self.scores.aggregate(avg=models.Avg("total_score"))["avg"]
        return round(avg, 1) if avg else None

    @property
    def recent_scores(self):
        return self.scores.order_by("-date")[:10]

    @property
    def handicap_progress(self):
        scores = self.scores.order_by("date")
        running = []
        for s in scores:
            if s.handicap_at_time is not None:
                running.append({"date": s.date.isoformat(), "handicap": float(s.handicap_at_time)})
        return running

    def calculate_handicap(self):
        """Delegate to Score.auto_calc_handicap for consistency."""
        last_score = self.scores.order_by("-date").first()
        if last_score:
            return last_score.auto_calc_handicap()
        return None


class Score(models.Model):
    LEAGUE_CHOICES = [
        ('all', 'All'),
        ('junior', 'Junior (Under 18)'),
        ('senior', 'Senior (55+)'),
        ('female', 'Female'),
    ]
    golfer = models.ForeignKey(GolferProfile, on_delete=models.CASCADE, related_name="scores")
    date = models.DateField()
    total_score = models.IntegerField()
    par = models.IntegerField(default=71)
    front_9 = models.IntegerField(null=True, blank=True)
    back_9 = models.IntegerField(null=True, blank=True)
    hole_scores = models.JSONField(default=dict, blank=True, help_text="Dict of hole_number: score (1-18)")
    handicap_at_time = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    league = models.CharField(max_length=10, choices=LEAGUE_CHOICES, default='all')
    course_conditions = models.CharField(max_length=30, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.golfer} - {self.total_score} on {self.date}"

    @property
    def to_par(self):
        return self.total_score - self.par

    @property
    def to_par_str(self):
        d = self.total_score - self.par
        if d < 0: return str(d)
        elif d == 0: return "E"
        else: return "+" + str(d)
    
    def auto_calc_handicap(self):
        """Calculate handicap from best 8 differentials of last 20 scores.
        Uses the WHS simplified method: average of 8 lowest score differentials × 0.96.
        Requires at least 3 scores. Returns 0 if average is negative."""
        golf = self.golfer
        last_20 = golf.scores.order_by("-date")[:20]
        count = last_20.count()
        if count < 3:
            return None
        # Score differentials (score - par), sorted lowest first
        diffs = sorted(s.total_score - s.par for s in last_20)
        
        # WHS-style: use fewer than 8 if fewer scores available
        best_count = min(8, max(1, count))
        best_n = diffs[:best_count]
        handicap = round(sum(best_n) / len(best_n) * 0.96, 1)
        return max(handicap, 0.0)  # Never negative


class WeeklyLeaderboard(models.Model):
    golfer = models.ForeignKey(GolferProfile, on_delete=models.CASCADE)
    score = models.IntegerField()
    week_start = models.DateField()
    week_end = models.DateField()

    class Meta:
        unique_together = ("golfer", "week_start")
        ordering = ["score"]

    def __str__(self):
        return f"{self.golfer} - {self.score} (w/c {self.week_start})"

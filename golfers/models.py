from django.db import models
from django.contrib.auth.models import User


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
        scores_qs = self.scores.order_by("-date")[:20]
        if scores_qs.count() < 3:
            return None
        best_scores = sorted(scores_qs, key=lambda s: s.total_score - s.par)[:8]
        if not best_scores:
            return None
        avg = sum(s.total_score - s.par for s in best_scores) / len(best_scores)
        return round(avg * 0.96, 1)


class Score(models.Model):
    golfer = models.ForeignKey(GolferProfile, on_delete=models.CASCADE, related_name="scores")
    date = models.DateField()
    total_score = models.IntegerField()
    par = models.IntegerField(default=71)
    front_9 = models.IntegerField(null=True, blank=True)
    back_9 = models.IntegerField(null=True, blank=True)
    handicap_at_time = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
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

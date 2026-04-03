from django.db import models

class TeeTime(models.Model):
    date = models.DateField()
    time = models.TimeField()
    is_available = models.BooleanField(default=True)
    max_players = models.IntegerField(default=4)
    booked_players = models.IntegerField(default=0)

    class Meta:
        ordering = ["date", "time"]
        unique_together = ("date", "time")

    @property
    def spots_remaining(self):
        return self.max_players - self.booked_players

class LessonSlot(models.Model):
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(default=45)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ["date", "time"]
        unique_together = ("date", "time")

class Booking(models.Model):
    tee_time = models.ForeignKey(TeeTime, on_delete=models.SET_NULL, null=True, blank=True)
    lesson_slot = models.ForeignKey(LessonSlot, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    num_players = models.IntegerField(default=1)
    player_names = models.TextField(default="")
    notes = models.TextField(blank=True, default="")
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        d = self.tee_time.date if self.tee_time else self.lesson_slot.date
        return f"{self.user.username} - {d}"

from django.db import models
from django.contrib.auth.models import User
import datetime

class TeeTime(models.Model):
    date = models.DateField()
    time = models.TimeField()
    is_available = models.BooleanField(default=True)
    max_players = models.IntegerField(default=4)
    booked_players = models.IntegerField(default=0)

    class Meta:
        ordering = ["date", "time"]
        unique_together = ("date", "time")

    def __str__(self):
        return f"{self.date} @ {self.time.strftime('%H:%M')}"

    @property
    def spots_remaining(self):
        return self.max_players - self.booked_players

class Booking(models.Model):
    tee_time = models.ForeignKey(TeeTime, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    num_players = models.IntegerField(default=1)
    player_names = models.TextField(help_text="Names of all players")
    notes = models.TextField(blank=True, default="")
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.tee_time.date}"

class LessonType(models.Model):
    name = models.CharField(max_length=100, default="PGA Lesson")
    duration_minutes = models.IntegerField(default=45)

    def __str__(self):
        return f"{self.name} ({self.duration_minutes} min)"

class LessonBooking(models.Model):
    date = models.DateField()
    time = models.TimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lesson_bookings")
    lesson_type = models.ForeignKey(LessonType, on_delete=models.CASCADE, default=1)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Lesson - {self.date}"

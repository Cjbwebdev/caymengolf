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

    def __str__(self):
        return f"{self.date} @ {self.time.strftime('%H:%M')}"

class Booking(models.Model):
    tee_time = models.ForeignKey(TeeTime, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="bookings")
    num_players = models.IntegerField(default=1)
    player_names = models.TextField()
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.tee_time.date}"

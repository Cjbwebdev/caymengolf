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

    @property
    def spots_remaining(self):
        return self.max_players - self.booked_players

class LessonSlot(models.Model):
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(default=45)
    is_available = models.BooleanField(default=True)
    booked_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="booked_lessons")

    class Meta:
        ordering = ["date", "time"]
        unique_together = ("date", "time")

    def __str__(self):
        return f"{self.date} @ {self.time.strftime('%H:%M')} (Lesson)"

class Booking(models.Model):
    BOOKING_TYPES = (
        ("tee_time", "Tee Time"),
        ("lesson", "PGA Lesson"),
    )
    tee_time = models.ForeignKey(TeeTime, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings")
    lesson_slot = models.ForeignKey(LessonSlot, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings")
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="bookings")
    num_players = models.IntegerField(default=1)
    player_names = models.TextField(help_text="Names of all players, one per line")
    notes = models.TextField(blank=True, default="")
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPES, default="tee_time")
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        date_str = self.tee_time.date if self.tee_time else (self.lesson_slot.date if self.lesson_slot else "N/A")
        time_str = self.tee_time.time.strftime('%H:%M') if self.tee_time else (self.lesson_slot.time.strftime('%H:%M') if self.lesson_slot else "")
        return f"{self.user.username} - {date_str} {time_str}"

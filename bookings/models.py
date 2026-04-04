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

    PRICE_PER_PLAYER = 25.00  # £25 per player
    
    @property
    def spots_remaining(self):
        return self.max_players - self.booked_players
    
    @property
    def price(self):
        return self.PRICE_PER_PLAYER

class LessonSlot(models.Model):
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(default=45)
    is_available = models.BooleanField(default=True)
    PRICE = 45.00  # £45 per lesson (45 mins with Dan)

    class Meta:
        ordering = ["date", "time"]
        unique_together = ("date", "time")
    
    @property
    def price(self):
        return self.PRICE

class Booking(models.Model):
    tee_time = models.ForeignKey(TeeTime, on_delete=models.SET_NULL, null=True, blank=True)
    lesson_slot = models.ForeignKey(LessonSlot, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    num_players = models.IntegerField(default=1)
    player_names = models.TextField(default="")
    notes = models.TextField(blank=True, default="")
    is_cancelled = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    stripe_session_id = models.CharField(max_length=300, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        d = self.tee_time.date if self.tee_time else self.lesson_slot.date
        return f"{self.user.username} - {d}"

from django.db import models

class LessonType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_minutes = models.IntegerField(default=60)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return self.name

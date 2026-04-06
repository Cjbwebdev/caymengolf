from django.db import models
from django.contrib.auth.models import User


class Invoice(models.Model):
    INVOICE_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    INVOICE_TYPE = [
        ('tee_time', 'Tee Time Booking'),
        ('lesson', 'Lesson Booking'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    booking = models.ForeignKey('bookings.Booking', on_delete=models.SET_NULL, null=True, blank=True)
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE)
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='pending')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.CharField(max_length=300, default='')
    stripe_session_id = models.CharField(max_length=300, blank=True, default='')
    stripe_payment_intent = models.CharField(max_length=300, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.invoice_type} - £{self.amount} - {self.status}'

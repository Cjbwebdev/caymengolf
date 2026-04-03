from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TeeTime, Booking
from django.utils import timezone

def booking_page(request):
    date_str = request.GET.get("date", str(timezone.now().date()))
    times = TeeTime.objects.filter(date=date_str, is_available=True).order_by("time")
    return render(request, "bookings/booking.html", {"tee_times": times, "selected_date": date_str})

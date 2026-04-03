from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import TeeTime, LessonSlot, Booking
from lessons.models import LessonType
from django.conf import settings
import datetime
from django.core.mail import send_mail

def booking_page(request):
    try:
        today = timezone.now().date()
        date_str = request.GET.get("date", str(today))
        selected_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

        # Ensure slots exist for this date
        if not TeeTime.objects.filter(date=selected_date).exists() and selected_date >= today and selected_date <= today + datetime.timedelta(days=14):
            _generate_tee_times(selected_date)

        times = TeeTime.objects.filter(date=selected_date, is_available=True).order_by("time")
        return render(request, "bookings/booking.html", {"tee_times": times, "selected_date": date_str})
    except Exception as e:
        # Fallback to a simple list view if anything goes wrong
        return render(request, "bookings/booking.html", {"tee_times": [], "selected_date": str(timezone.now().date()), "error": str(e)})

def _generate_tee_times(date):
    current = datetime.time(8, 0)
    while current.hour < 17 or (current.hour == 17 and current.minute <= 30):
        TeeTime.objects.create(date=date, time=current, max_players=4, booked_players=0)
        current = (datetime.datetime.combine(date, current) + datetime.timedelta(minutes=10)).time()

@login_required
def book_slot(request, time_id):
    tee_time = get_object_or_404(TeeTime, pk=time_id)
    if not tee_time.is_available:
        messages.error(request, "Slot taken.")
        return redirect("bookings:booking")
    if request.method == "POST":
        num = int(request.POST.get("num_players", 1))
        players = request.POST.get("player_names", request.user.username)
        Booking.objects.create(tee_time=tee_time, user=request.user, num_players=num, player_names=players)
        tee_time.booked_players += num
        if tee_time.booked_players >= tee_time.max_players: tee_time.is_available = False
        tee_time.save()
        
        # Email Dan
        try: send_mail("New Booking", f"Booking for {num} on {tee_time.date} at {tee_time.time}", "support@cjbwebdevelopment.com", ["danleins@hotmail.co.uk"], fail_silently=True)
        except: pass
        
        messages.success(request, "Slot confirmed!")
        return redirect("golfers:my_profile")
    return render(request, "bookings/confirm.html", {"tee_time": tee_time})

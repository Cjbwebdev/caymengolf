from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from .models import TeeTime, LessonSlot, Booking
import datetime

def booking_page(request):
    today = timezone.now().date()
    date_str = request.GET.get("date", str(today))
    try:
        selected_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        selected_date = today
        
    if not TeeTime.objects.filter(date=selected_date).exists() and selected_date >= today and selected_date <= today + datetime.timedelta(days=14):
        current = datetime.time(8, 0)
        while current.hour < 17 or (current.hour == 17 and current.minute <= 30):
            TeeTime.objects.create(date=selected_date, time=current, max_players=4, booked_players=0)
            current = (datetime.datetime.combine(selected_date, current) + datetime.timedelta(minutes=10)).time()
    
    times = TeeTime.objects.filter(date=selected_date, is_available=True).order_by("time")
    return render(request, "bookings/booking.html", {"tee_times": times, "selected_date": date_str})

@login_required
def book_slot(request, time_id):
    tee_time = get_object_or_404(TeeTime, pk=time_id)
    if not tee_time.is_available:
        messages.error(request, "Sorry, this slot has been taken.")
        return redirect("bookings:booking")
        
    if request.method == "POST":
        num_players = int(request.POST.get("num_players", 1))
        if num_players > tee_time.spots_remaining:
            messages.error(request, f"Only {tee_time.spots_remaining} spots remaining.")
            return redirect("bookings:book_slot", time_id=tee_time.pk)
            
        players = request.POST.get("player_names", request.user.username)
        notes = request.POST.get("notes", "")
        
        Booking.objects.create(
            tee_time=tee_time,
            user=request.user,
            num_players=num_players,
            player_names=players,
            notes=notes,
            booking_type="tee_time"
        )
        
        # Email Dan
        try: send_mail("New Booking", f"Booking for {num_players} on {tee_time.date} at {tee_time.time}", "support@cjbwebdevelopment.com", ["danleins@hotmail.co.uk"], fail_silently=True)
        except: pass
        
        tee_time.booked_players += num_players
        if tee_time.booked_players >= tee_time.max_players: tee_time.is_available = False
        tee_time.save()
        
        messages.success(request, "Slot confirmed!")
        return redirect("golfers:my_profile")
    return render(request, "bookings/confirm.html", {"tee_time": tee_time})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "bookings/my_bookings.html", {"bookings": bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if booking.tee_time:
        tee_time = booking.tee_time
        tee_time.is_available = True
        tee_time.booked_players = max(0, tee_time.booked_players - booking.num_players)
        tee_time.save()
        booking.is_cancelled = True
        booking.save()
        messages.success(request, "Booking cancelled.")
    return redirect("golfers:my_profile")

def lesson_page(request):
    return render(request, "pages/lessons.html")

@login_required
def book_lesson(request, slot_id):
    messages.success(request, "Lesson booking confirmed (Placeholder - Email sent to Dan)")
    return redirect("bookings:my_bookings")

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import TeeTime, Booking

def booking_page(request):
    date_str = request.GET.get("date", str(timezone.now().date()))
    times = TeeTime.objects.filter(date=date_str, is_available=True).order_by("time")[:30]
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
            return redirect("bookings:booking")
            
        players = request.POST.get("player_names", request.user.username)
        notes = request.POST.get("notes", "")
        
        Booking.objects.create(
            tee_time=tee_time,
            user=request.user,
            num_players=num_players,
            player_names=players,
            notes=notes,
        )
        
        tee_time.booked_players += num_players
        if tee_time.booked_players >= tee_time.max_players:
            tee_time.is_available = False
        tee_time.save()
        
        messages.success(request, f"✅ Tee time confirmed for {tee_time.date} at {tee_time.time.strftime('%H:%M')}!")
        return redirect("golfers:my_profile")
        
    return render(request, "bookings/confirm.html", {"tee_time": tee_time})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user, is_cancelled=False).order_by("-created_at")
    return render(request, "bookings/my_bookings.html", {"bookings": bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    if booking.tee_time.date < timezone.now().date():
        messages.error(request, "Cannot cancel a past booking.")
        return redirect("bookings:my_bookings")
        
    # Free up the spots
    tee_time = booking.tee_time
    tee_time.is_available = True
    tee_time.booked_players = max(0, tee_time.booked_players - booking.num_players)
    tee_time.save()
    
    booking.is_cancelled = True
    booking.save()
    
    messages.success(request, "Booking cancelled successfully.")
    return redirect("bookings:my_bookings")

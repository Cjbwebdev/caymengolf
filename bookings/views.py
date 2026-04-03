from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import TeeTime, LessonSlot, Booking
import datetime

def booking_page(request):
    today = timezone.now().date()
    date_str = request.GET.get("date", str(today))
    
    try:
        selected_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        selected_date = today

    # Auto-generate TeeTime slots if none exist
    if TeeTime.objects.filter(date=selected_date).count() == 0:
        current_min = 8 * 60 # 08:00 in minutes
        end_min = 17 * 60 + 30 # 17:30 in minutes
        while current_min <= end_min:
            h, m = divmod(current_min, 60)
            TeeTime.objects.create(date=selected_date, time=datetime.time(h, m), max_players=4)
            current_min += 10 # 10 minute intervals

    times = TeeTime.objects.filter(date=selected_date).order_by("time")

    # Filter out past slots for today
    if selected_date == today:
        current_min = timezone.now().hour * 60 + timezone.now().minute
        times = times.filter(time__gte=datetime.time(current_min // 60, current_min % 60))

    return render(request, "bookings/booking.html", {
        "tee_times": times, 
        "selected_date": date_str,
        "min_date": str(today)
    })

@login_required
def book_slot(request, time_id):
    tee_time = get_object_or_404(TeeTime, pk=time_id)
    if not tee_time.is_available:
        messages.error(request, "Slot taken.")
        return redirect("bookings:booking")
        
    if request.method == "POST":
        num = int(request.POST.get("num_players", 1))
        if num > tee_time.spots_remaining:
            messages.error(request, f"Only {tee_time.spots_remaining} spots left.")
            return redirect("bookings:book_slot", time_id=tee_time.pk)
            
        Booking.objects.create(tee_time=tee_time, user=request.user, num_players=num, player_names=request.POST.get("player_names", ""))
        
        tee_time.booked_players += num
        if tee_time.booked_players >= tee_time.max_players: tee_time.is_available = False
        tee_time.save()
        
        # Email Dan
        try: send_mail("New Booking", f"Tee time for {num} on {tee_time.date} at {tee_time.time}", "support@cjbwebdevelopment.com", ["danleins@hotmail.co.uk"], fail_silently=True)
        except: pass
        
        messages.success(request, "Tee time confirmed!")
        return redirect("golfers:my_profile")
        
    return render(request, "bookings/confirm.html", {"tee_time": tee_time})

def lessons_page(request):
    today = timezone.now().date()
    date_str = request.GET.get("date", str(today))
    
    try:
        selected_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        selected_date = today

    # Auto-generate Lesson Slots (45 mins) if none exist
    if LessonSlot.objects.filter(date=selected_date).count() == 0:
        current_min = 8 * 60 # 08:00
        end_min = 17 * 60 + 30
        while current_min + 45 <= end_min: # Ensure full 45 min slot fits
            h, m = divmod(current_min, 60)
            LessonSlot.objects.create(date=selected_date, time=datetime.time(h, m), duration=45)
            current_min += 45 

    slots = LessonSlot.objects.filter(date=selected_date, is_available=True).order_by("time")

    # Filter out past slots for today
    if selected_date == today:
        current_min = timezone.now().hour * 60 + timezone.now().minute
        slots = slots.filter(time__gte=datetime.time(current_min // 60, current_min % 60))

    return render(request, "pages/lessons.html", {
        "available_slots": slots, 
        "selected_date": date_str,
        "min_date": str(today)
    })

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user, is_cancelled=False).order_by("-created_at")
    return render(request, "bookings/my_bookings.html", {"bookings": bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if booking.tee_time:
        booking.tee_time.is_available = True
        booking.tee_time.save()
    booking.is_cancelled = True
    booking.save()
    return redirect("golfers:my_profile")

@login_required
def book_lesson(request, slot_id):
    slot = get_object_or_404(LessonSlot, pk=slot_id)
    if request.method == "POST":
        Booking.objects.create(
            lesson_slot=slot, 
            user=request.user, 
            num_players=1, 
            player_names=request.user.username,
            notes=request.POST.get("notes", "")
        )
        slot.is_available = False
        slot.save()
        try: send_mail("New Lesson", f"Lesson booking on {slot.date} at {slot.time}", "support@cjbwebdevelopment.com", ["danleins@hotmail.co.uk"], fail_silently=True)
        except: pass
        messages.success(request, "Lesson confirmed with Dan!")
        return redirect("bookings:my_bookings")
    return render(request, "bookings/lesson_confirm.html", {"slot": slot})

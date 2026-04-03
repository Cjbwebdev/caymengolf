from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from .models import TeeTime, LessonSlot, Booking
from lessons.models import LessonType
import datetime

def booking_page(request):
    date_str = request.GET.get("date", str(timezone.now().date()))
    try:
        selected_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        selected_date = timezone.now().date()
        
    today = timezone.now().date()
    
    # Auto-generate slots for this date if they don't exist
    if not TeeTime.objects.filter(date=selected_date).exists() and selected_date >= today and selected_date <= today + datetime.timedelta(days=14):
        current = datetime.time(8, 0)
        while current.hour < 17 or (current.hour == 17 and current.minute <= 30):
            TeeTime.objects.get_or_create(date=selected_date, time=current, defaults={"max_players": 4, "booked_players": 0})
            current = (datetime.datetime.combine(selected_date, current) + datetime.timedelta(minutes=10)).time()
    
    times = TeeTime.objects.filter(date=selected_date, is_available=True).order_by("time")
    
    # Filter out past slots for today
    if selected_date == today:
        # NUCLEAR OPTION: Physically delete past slots so they NEVER show up
        now = timezone.now().time()
        cutoff = (datetime.datetime.combine(today, now) - datetime.timedelta(minutes=5)).time()
        TeeTime.objects.filter(date=today, time__lt=cutoff).delete()
        now = timezone.now().time()
        # Give a 5-min buffer
        times = times.filter(
            time__gte=(datetime.datetime.combine(selected_date, now) - datetime.timedelta(minutes=5)).time()
        )
    
    return render(request, "bookings/booking.html", {"tee_times": times, "selected_date": date_str, "max_date": (today + datetime.timedelta(days=14)).isoformat()})

@login_required
def book_slot(request, time_id):
    tee_time = get_object_or_404(TeeTime, pk=time_id)
    
    if not tee_time.is_available:
        messages.error(request, "Sorry, this slot has been taken.")
        return redirect("bookings:booking")
    
    if request.method == "POST":
        num_players = int(request.POST.get("num_players", 1))
        if num_players > tee_time.spots_remaining or num_players < 1:
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
        
        # Send email to Dan
        try:
            send_mail(
                subject=f"New Tee Time Booking - {tee_time.date} at {tee_time.time.strftime('%H:%M')}",
                message=f"Booking for {num_players} player(s) on {tee_time.date} at {tee_time.time.strftime('%H:%M')}\n\n"
                        f"Booked by: {request.user.username} ({request.user.email})\n"
                        f"Player(s): {players}\n"
                        f"Notes: {notes}\n\n"
                        f"Please reply to confirm.",
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@caymangolf.site"),
                recipient_list=["danleins@hotmail.co.uk"],
                fail_silently=True,
            )
        except Exception:
            pass  # Email failing shouldn't break the booking
        
        tee_time.booked_players += num_players
        if tee_time.booked_players >= tee_time.max_players:
            tee_time.is_available = False
        tee_time.save()
        
        messages.success(request, f"✅ Tee time confirmed for {tee_time.date} at {tee_time.time.strftime('%H:%M')}!")
        return redirect("bookings:my_bookings")
        
    return render(request, "bookings/confirm.html", {"tee_time": tee_time})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "bookings/my_bookings.html", {"bookings": bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    if booking.booking_type == "lesson":
        try:
            slot = booking.lesson_slot
            slot.is_available = True
            slot.save()
        except: pass
    else:
        try:
            tee_time = booking.tee_time
            tee_time.is_available = True
            tee_time.booked_players = max(0, tee_time.booked_players - booking.num_players)
            tee_time.save()
        except: pass
    
    booking.is_cancelled = True
    booking.save()
    
    messages.success(request, "Booking cancelled successfully.")
    return redirect("bookings:my_bookings")


# ─── Lesson Booking ───
def lesson_page(request):
    date_str = request.GET.get("date", str(timezone.now().date()))
    try:
        selected_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        selected_date = timezone.now().date()
    
    today = timezone.now().date()
    
    # Auto-generate 45-min lesson slots if they don't exist
    # Always ensure slots exist for the view
    if selected_date == today:
        now = timezone.now().time()
        cutoff = (datetime.datetime.combine(today, now) - datetime.timedelta(minutes=5)).time()
        LessonSlot.objects.filter(date=today, time__lt=cutoff).delete()
        
    if not LessonSlot.objects.filter(date=selected_date).exists() and selected_date >= today and selected_date <= today + datetime.timedelta(days=14):
        current = datetime.time(8, 0)
        while (current.hour * 60 + current.minute + 45) <= (17 * 60 + 30):
            LessonSlot.objects.get_or_create(date=selected_date, time=current, defaults={"duration": 45})
            current = (datetime.datetime.combine(selected_date, current) + datetime.timedelta(minutes=45)).time()
    
    available_slots = LessonSlot.objects.filter(date=selected_date, is_available=True).order_by("time")
    
    # Filter out past for today
    if selected_date == today:
        # NUCLEAR OPTION: Physically delete past slots so they NEVER show up
        now = timezone.now().time()
        cutoff = (datetime.datetime.combine(today, now) - datetime.timedelta(minutes=5)).time()
        TeeTime.objects.filter(date=today, time__lt=cutoff).delete()
        now = timezone.now().time()
        available_slots = available_slots.filter(
            time__gte=(datetime.datetime.combine(selected_date, now) - datetime.timedelta(minutes=5)).time()
        )
    
    return render(request, "pages/lessons.html", {
        "available_slots": available_slots, 
        "selected_date": date_str,
        "max_date": (today + datetime.timedelta(days=14)).isoformat()
    })

@login_required
def book_lesson(request, slot_id):
    slot = get_object_or_404(LessonSlot, pk=slot_id)
    
    if not slot.is_available or slot.date < timezone.now().date():
        messages.error(request, "This lesson slot is not available.")
        return redirect("pages:lessons")
    
    if request.method == "POST":
        notes = request.POST.get("skill_level", "") + "\n" + request.POST.get("notes", "")
        
        Booking.objects.create(
            lesson_slot=slot,
            user=request.user,
            num_players=1,
            player_names=request.user.username,
            notes=notes,
            booking_type="lesson"
        )
        
        # Send email to Dan
        try:
            send_mail(
                subject=f"New Lesson Booking - {slot.date} at {slot.time.strftime('%H:%M')}",
                message=f"Lesson for {slot.duration} minutes on {slot.date} at {slot.time.strftime('%H:%M')}\n\n"
                        f"Student: {request.user.username} ({request.user.email})\n"
                        f"Skill/Notes: {notes}\n\n"
                        f"Please reply to confirm.",
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@caymangolf.site"),
                recipient_list=["danleins@hotmail.co.uk"],
                fail_silently=True,
            )
        except Exception:
            pass
        
        slot.is_available = False
        slot.booked_by = request.user
        slot.save()
        
        messages.success(request, f"✅ Lesson confirmed with Dan on {slot.date} at {slot.time.strftime('%H:%M')}!")
        return redirect("bookings:my_bookings")
    
    return render(request, "bookings/lesson_confirm.html", {"slot": slot})

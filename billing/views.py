import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from bookings.models import TeeTime, LessonSlot, Booking

if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY

SITE_URL = "https://caymangolf.site"


@login_required
def checkout_session(request, booking_id=None):
    # Accept booking_id from URL path or GET parameter
    if not booking_id:
        booking_id = request.GET.get("booking")
    if not booking_id:
        messages.error(request, "No booking selected for payment.")
        return redirect("home")
    
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        messages.error(request, "Booking not found.")
        return redirect("home")
    
    # Determine amount based on booking
    if booking.total_price:
        amount_pence = int(float(booking.total_price) * 100)
    elif booking.tee_time:
        amount_pence = int(float(booking.tee_time.price) * booking.num_players * 100)
    else:
        amount_pence = 4500  # Default lesson price
    
    if booking.tee_time:
        item_name = f"Tee Time - {booking.tee_time.date} at {booking.tee_time.time}"
    elif booking.lesson_slot:
        item_name = f"Lesson - {booking.lesson_slot.date} at {booking.lesson_slot.time} (45 mins)"
    else:
        item_name = "Golf Booking"
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "gbp",
                    "product_data": {"name": item_name},
                    "unit_amount": amount_pence,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{SITE_URL}/billing/success/?session_id=" + "{CHECKOUT_SESSION_ID}",
            cancel_url=f"{SITE_URL}/bookings/my-bookings/",
            customer_email=request.user.email,
            metadata={"booking_id": str(booking.id)},
        )
        booking.stripe_session_id = session.id
        booking.save()
        return redirect(session.url)
    except Exception as e:
        messages.error(request, f"Payment error: {str(e)}")
        return redirect("home")


@login_required
def payment_success(request):
    session_id = request.GET.get("session_id")
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                booking_id = session.metadata.get("booking_id")
                if booking_id:
                    booking = Booking.objects.get(id=booking_id)
                    booking.is_paid = True
                    booking.save()
                messages.success(request, "Payment successful! Your booking is confirmed.")
            else:
                messages.warning(request, "Payment is still pending.")
        except Exception as e:
            messages.error(request, f"Error verifying payment: {str(e)}")
    
    return redirect("my_bookings")


def webhook(request):
    payload = request.body
    sig = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return redirect("home", status=400)
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        booking_id = session.get("metadata", {}).get("booking_id")
        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                booking.is_paid = True
                booking.save()
                
                # Send confirmation email
                from django.core.mail import send_mail
                send_mail(
                    subject=f"Your Golf Booking is Confirmed - Cayman Golf Brixham",
                    message=f"Hi {booking.user.username},\n\nYour booking on {booking.tee_time.date if booking.tee_time else booking.lesson_slot.date} is confirmed and paid.\n\nThank you for choosing Cayman Golf Brixham!",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[booking.user.email],
                )
            except Exception as e:
                print(f"Webhook processing error: {e}")
    
    return redirect("home", status=200)


@login_required
def my_invoices(request):
    from billing.models import Invoice
    invoices = Invoice.objects.filter(user=request.user)
    return render(request, "billing/invoices.html", {"invoices": invoices})

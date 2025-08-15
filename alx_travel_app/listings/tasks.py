from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_payment_confirmation(email, booking_reference):
    send_mail(
        "Payment Confirmation",
        f"Your payment for booking {booking_reference} was successful.",
        "no-reply@travelapp.com",
        [email],
        fail_silently=False,
    )

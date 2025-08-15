from rest_framework import viewsets
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
import uuid
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from .models import Payment
import requests

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer



class InitiatePaymentView(View):
    def post(self, request, *args, **kwargs):
        # Extract booking details from request body
        data = request.POST
        amount = data.get("amount")
        email = data.get("email")
        first_name = data.get("first_name", "Guest")
        last_name = data.get("last_name", "")

        # Create unique booking reference
        booking_reference = str(uuid.uuid4())

        # Create payment entry
        payment = Payment.objects.create(
            booking_reference=booking_reference,
            amount=amount
        )

        payload = {
            "amount": str(amount),
            "currency": "ETB",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": booking_reference,
            "callback_url": "http://localhost:8000/api/payments/verify/",
            "return_url": "http://localhost:8000/payment-success/",
            "customization[title]": "Travel Booking Payment",
            "customization[description]": "Payment for your travel booking"
        }

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(f"{settings.CHAPA_BASE_URL}/transaction/initialize", 
                                 json=payload, headers=headers)

        resp_json = response.json()
        if resp_json.get("status") == "success":
            payment.transaction_id = booking_reference
            payment.save()
            return JsonResponse({"payment_url": resp_json["data"]["checkout_url"]})
        else:
            payment.status = "Failed"
            payment.save()
            return JsonResponse({"error": "Payment initiation failed"}, status=400)
        


class VerifyPaymentView(View):
    def get(self, request, *args, **kwargs):
        tx_ref = request.GET.get("tx_ref")
        try:
            payment = Payment.objects.get(booking_reference=tx_ref)
        except Payment.DoesNotExist:
            return JsonResponse({"error": "Payment not found"}, status=404)

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
        }

        response = requests.get(f"{settings.CHAPA_BASE_URL}/transaction/verify/{tx_ref}", 
                                headers=headers)
        resp_json = response.json()

        if resp_json.get("status") == "success" and resp_json["data"]["status"] == "success":
            payment.status = "Completed"
            payment.save()
            #  Trigger Celery email notification
            return JsonResponse({"message": "Payment successful"})
        else:
            payment.status = "Failed"
            payment.save()
            return JsonResponse({"message": "Payment failed"}, status=400)

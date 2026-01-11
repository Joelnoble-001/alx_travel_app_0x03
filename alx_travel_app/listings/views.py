from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer
import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tasks import send_booking_email


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        booking = serializer.save()
        # Trigger the email asynchronously
        send_booking_email.delay(booking.id, booking.user.email)



@api_view(["POST"])
def initiate_payment(request):
    booking_ref = request.data.get("booking_reference")
    amount = request.data.get("amount")
    email = request.data.get("email")

    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": email,
        "tx_ref": booking_ref,
        "callback_url": "http://localhost:8000/api/payment/verify/",
        "return_url": "http://localhost:8000/payment-success/",
        "customization": {
            "title": "Travel Booking Payment",
        },
    }

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{settings.CHAPA_BASE_URL}/transaction/initialize",
        json=payload,
        headers=headers,
    )

    data = response.json()

    if response.status_code == 200:
        Payment.objects.create(
            booking_reference=booking_ref,
            transaction_id=data["data"]["tx_ref"],
            amount=amount,
            status="Pending",
        )
        return Response(
            {"payment_url": data["data"]["checkout_url"]},
            status=status.HTTP_200_OK,
        )

    return Response(data, status=status.HTTP_400_BAD_REQUEST)

# verify payment

@api_view(["GET"])
def verify_payment(request):
    tx_ref = request.GET.get("tx_ref")

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
    }

    response = requests.get(
        f"{settings.CHAPA_BASE_URL}/transaction/verify/{tx_ref}",
        headers=headers,
    )

    data = response.json()

    try:
        payment = Payment.objects.get(transaction_id=tx_ref)

        if data["data"]["status"] == "success":
            payment.status = "Completed"
        else:
            payment.status = "Failed"

        payment.save()
        return Response({"status": payment.status})

    except Payment.DoesNotExist:
        return Response(
            {"error": "Payment not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

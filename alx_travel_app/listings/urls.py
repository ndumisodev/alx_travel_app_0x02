from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ListingViewSet, BookingViewSet
from .views import InitiatePaymentView, VerifyPaymentView


router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path("payments/initiate/", InitiatePaymentView.as_view(), name="initiate-payment"),
    path("payments/verify/", VerifyPaymentView.as_view(), name="verify-payment"),
]

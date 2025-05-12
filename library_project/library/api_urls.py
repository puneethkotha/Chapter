from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'books', views.BookViewSet)
router.register(r'rentals', views.RentalViewSet, basename='rental')
router.register(r'events', views.EventViewSet)
router.register(r'study-rooms', views.StudyRoomViewSet)
router.register(r'reservations', views.ReservationViewSet, basename='reservation')
router.register(r'customers', views.CustomerViewSet)
router.register(r'invoices', views.InvoiceViewSet, basename='invoice')
router.register(r'payments', views.PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
] 
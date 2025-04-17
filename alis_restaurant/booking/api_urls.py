from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'tables', api_views.TableViewSet)
router.register(r'bookings', api_views.BookingViewSet, basename='booking')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/available-tables/', api_views.AvailableTablesAPIView.as_view(), name='api_available_tables'),
]


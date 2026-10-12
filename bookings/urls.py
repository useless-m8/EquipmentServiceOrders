from django.urls import path

from bookings import views

urlpatterns = [
    path("", views.booking_list, name="booking_list"),
    path("<int:booking_id>/", views.booking_detail,
         name="booking_detail"),
]

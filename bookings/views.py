from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from core.services import find_by_id
from core.storage import load_project_data


def booking_list(request: HttpRequest) -> HttpResponse:
    try:
        _, _, bookings = load_project_data(
            getattr(settings, "SERVICE_DATA_FILE", None)
        )
    except (OSError, ValueError):
        return HttpResponse("Не удалось прочитать бронирования.", status=500)
    return render(request, "bookings/list.html", {
        "title": "Бронирования",
        "bookings": bookings,
    })


def booking_detail(
    request: HttpRequest, booking_id: int,
) -> HttpResponse:
    try:
        _, _, bookings = load_project_data(
            getattr(settings, "SERVICE_DATA_FILE", None)
        )
    except (OSError, ValueError):
        return HttpResponse("Не удалось прочитать бронирования.", status=500)
    try:
        booking = find_by_id(bookings, booking_id)
    except ValueError:
        return HttpResponse("Бронирование не найдено.", status=404)
    return render(request, "bookings/detail.html", {
        "title": f"Бронирование №{booking.id}",
        "booking": booking,
    })

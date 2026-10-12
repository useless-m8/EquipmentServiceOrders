from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import escape

from homepage.views import page
from core.services import find_by_id
from core.storage import load_project_data


def booking_list(request: HttpRequest) -> HttpResponse:
    try:
        _, _, bookings = load_project_data(
            getattr(settings, "SERVICE_DATA_FILE", None)
        )
    except (OSError, ValueError):
        return HttpResponse("Не удалось прочитать бронирования.", status=500)
    cards = []
    for booking in bookings:
        color = "secondary" if booking.is_cancelled else "success"
        cards.append(
            f'<li class="list-group-item d-flex justify-content-between">'
            f'<a href="{reverse("booking_detail", args=[booking.id])}">'
            f'#{booking.id} · {escape(booking.equipment.name)} · '
            f'{escape(str(booking.period))}</a>'
            f'<span class="badge text-bg-{color}">'
            f'{booking.status}</span></li>'
        )
    cards_html = "".join(cards)
    if not cards_html:
        cards_html = '<li class="list-group-item">Бронирований пока нет.</li>'
    content = (
        '<h1 class="mb-3">Бронирования</h1>'
        '<ul class="list-group">'
        f"{cards_html}</ul>"
    )
    return HttpResponse(page("Бронирования", content))


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
    color = "secondary" if booking.is_cancelled else "success"
    content = f"""
<a href="{reverse('booking_list')}" class="btn btn-link px-0">
← Бронирования</a>
<div class="card"><div class="card-body">
<h1>Бронирование №{booking.id}</h1>
<p>Пользователь: {escape(booking.user.name)}</p>
<p>Оборудование:
<a href="{reverse('equipment_detail', args=[booking.equipment.id])}">
{escape(booking.equipment.name)}</a></p>
<p>Период: {escape(str(booking.period))}</p>
<p>Стоимость: {booking.cost:.2f} руб.</p>
<p>Статус: <span class="badge text-bg-{color}">{booking.status}</span></p>
</div></div>
"""
    return HttpResponse(page(f"Бронирование №{booking.id}", content))

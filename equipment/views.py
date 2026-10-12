from datetime import datetime, timedelta

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape

from homepage.views import page
from core.models import Period
from core.services import (
    filter_available,
    find_by_id,
    is_available,
    sort_equipment,
)
from core.storage import load_project_data


def equipment_list(request: HttpRequest) -> HttpResponse:
    try:
        _, equipment, bookings = load_project_data(
            getattr(settings, "SERVICE_DATA_FILE", None)
        )
    except (OSError, ValueError):
        return HttpResponse(
            "Не удалось прочитать список оборудования.", status=500
        )
    cards = []
    for item in sort_equipment(equipment):
        status = "Исправно" if item.is_working else "На ремонте"
        cards.append(
            f'<div class="col"><div class="card h-100"><div class="card-body">'
            f'<h2 class="h5">{escape(item.name)}</h2>'
            f'<p>{item.hourly_rate:.2f} руб./час</p>'
            f'<p>{status}</p>'
            f'<a class="btn btn-outline-primary" href="'
            f'{reverse("equipment_detail", args=[item.id])}">Подробнее</a>'
            "</div></div></div>"
        )
    count = len(filter_available(equipment, default_period(), bookings))
    content = (
        '<h1 class="mb-3">Оборудование</h1>'
        f'<p>Доступно на ближайший час: {count}</p>'
        f'<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">'
        f'{"".join(cards) or "<p>Оборудование пока не добавлено.</p>"}</div>'
    )
    return HttpResponse(page("Оборудование", content))


def default_period() -> Period:
    now = timezone.localtime().replace(tzinfo=None, second=0, microsecond=0)
    return Period(now, now + timedelta(hours=1))


def equipment_detail(
    request: HttpRequest, equipment_id: int,
) -> HttpResponse:
    try:
        _, equipment, bookings = load_project_data(
            getattr(settings, "SERVICE_DATA_FILE", None)
        )
    except (OSError, ValueError):
        return HttpResponse(
            "Не удалось прочитать список оборудования.", status=500
        )
    try:
        item = find_by_id(equipment, equipment_id)
    except ValueError:
        return HttpResponse("Оборудование не найдено.", status=404)
    period = default_period()
    error = ""
    start_value = request.GET.get("start", "")
    end_value = request.GET.get("end", "")
    if start_value or end_value:
        try:
            if not start_value or not end_value:
                raise ValueError("Заполните начало и конец периода.")
            period = Period(
                datetime.fromisoformat(start_value),
                datetime.fromisoformat(end_value),
            )
        except ValueError as exc:
            error = str(exc)
    available = is_available(item, period, bookings)
    state = "Доступно" if available else "Занято или неисправно"
    check_form = f"""
<form class="row g-3 mb-4" method="get">
<div class="col-md-5"><label class="form-label" for="start">Начало</label>
<input class="form-control" id="start" name="start" type="datetime-local"
value="{escape(start_value)}"></div>
<div class="col-md-5"><label class="form-label" for="end">Окончание</label>
<input class="form-control" id="end" name="end" type="datetime-local"
value="{escape(end_value)}"></div>
<div class="col-md-2 align-self-end">
<button class="btn btn-primary">Проверить</button></div>
</form>
"""
    content = f"""
<a href="{reverse('equipment_list')}" class="btn btn-link px-0">← Оборудование</a>
<div class="card"><div class="card-body">
<h1>{escape(item.name)}</h1>
<p>Тариф: {item.hourly_rate:.2f} руб./час</p>
<p>Состояние: {'исправно' if item.is_working else 'на ремонте'}</p>
<h2 class="h5 mt-4">Проверить свободное время</h2>
{check_form}
{f'<p class="text-danger">{escape(error)}</p>' if error else ''}
<p>{escape(str(period))}: <strong>{state}</strong></p>
<p>Стоимость: {item.calculate_cost(period):.2f} руб.</p>
</div></div>
"""
    return HttpResponse(page(item.name, content))

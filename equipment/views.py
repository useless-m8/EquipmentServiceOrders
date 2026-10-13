from datetime import datetime, timedelta

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

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
    return render(request, "equipment/list.html", {
        "title": "Оборудование",
        "equipment": sort_equipment(equipment),
        "available_count": len(filter_available(
            equipment, default_period(), bookings
        )),
    })


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
    return render(request, "equipment/detail.html", {
        "title": item.name,
        "item": item,
        "period": period,
        "available": is_available(item, period, bookings),
        "cost": item.calculate_cost(period),
        "error": error,
        "start_value": start_value,
        "end_value": end_value,
    })

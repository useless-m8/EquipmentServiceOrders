from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "homepage/index.html", {
        "title": "Бронирование оборудования",
    })


def page_not_found(
    request: HttpRequest, exception: Exception,
) -> HttpResponse:
    return render(request, "404.html", {
        "title": "Страница не найдена",
    }, status=404)

from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import escape


def page(title: str, content: str) -> str:
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/"
        "dist/css/bootstrap.min.css"
    )
    navigation = (
        f'<a class="nav-link" href="{reverse("index")}">Главная</a>'
        f'<a class="nav-link" href="{reverse("equipment_list")}">'
        "Оборудование</a>"
        f'<a class="nav-link" href="{reverse("booking_list")}">'
        "Бронирования</a>"
    )
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<link href="{bootstrap}" rel="stylesheet">
<style>
body {{ background: #f5f7fa; color: #263238; }}
.navbar {{ background: white; }}
.card {{ border: 0; box-shadow: 0 3px 14px #132a3a12; }}
.container {{ max-width: 1080px; }}
</style>
</head>
<body>
<nav class="navbar navbar-expand navbar-light border-bottom mb-4">
<div class="container">
<a class="navbar-brand fw-semibold" href="{reverse("index")}">Прокат</a>
<div class="navbar-nav">{navigation}</div>
</div>
</nav>
<main class="container pb-5">{content}</main>
</body>
</html>"""


def index(request: HttpRequest) -> HttpResponse:
    content = """
<section class="p-5 mb-4 bg-white rounded-3">
<h1 class="display-5 fw-semibold">Бронирование оборудования</h1>
<p class="lead">Выберите технику и проверьте, свободна ли она на
нужное время.</p>
<a class="btn btn-primary me-2" href="/equipment/">Оборудование</a>
<a class="btn btn-outline-primary" href="/bookings/">Бронирования</a>
</section>
"""
    return HttpResponse(page("Бронирование оборудования", content))


def page_not_found(
    request: HttpRequest, exception: Exception,
) -> HttpResponse:
    content = """
<div class="text-center bg-white rounded-3 p-5">
<h1 class="text-danger">404 — страница не найдена</h1>
<p>Проверьте адрес или вернитесь к списку оборудования.</p>
<a class="btn btn-primary" href="/equipment/">Оборудование</a>
</div>
"""
    return HttpResponse(page("Страница не найдена", content), status=404)

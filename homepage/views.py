from django.http import HttpRequest, HttpResponse
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import escape


def page(title: str, content: str) -> str:
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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="{static('homepage/style.css')}" rel="stylesheet">
</head>
<body>
<nav class="site-nav">
<div class="container nav-inner">
<a class="brand" href="{reverse("index")}"><span class="brand-mark">Э</span><span>Технопрокат</span></a>
<div class="nav-links">{navigation}</div>
</div>
</nav>
<main class="container main-content">{content}</main>
<footer class="site-footer"><div class="container">Сервис бронирования оборудования</div></footer>
</body>
</html>"""


def index(request: HttpRequest) -> HttpResponse:
    content = """
<section class="hero">
<div class="hero-copy">
<span class="eyebrow"><span class="eyebrow-dot"></span>Техника рядом, когда нужна</span>
<h1>Нужное оборудование<br>в нужное время</h1>
<p>Выбирайте технику, проверяйте свободные даты и планируйте работу без лишних хлопот.</p>
<div class="hero-actions">
<a class="button button-primary" href="/equipment/">Выбрать оборудование <span>→</span></a>
<a class="button button-light" href="/bookings/">Мои бронирования</a>
</div>
<div class="hero-note"><span class="note-icon">✓</span>Доступность можно проверить до бронирования</div>
</div>
<div class="hero-art" aria-hidden="true">
<div class="art-orbit orbit-one"></div><div class="art-orbit orbit-two"></div>
<div class="art-card"><span class="art-label">В работе</span><div class="projector"><div class="projector-lens"></div><div class="projector-line"></div><div class="projector-line short"></div></div><div class="art-caption"><span>Проектор Epson</span><span class="art-status"><i></i> Исправен</span></div></div>
<span class="art-spark spark-one">✳</span><span class="art-spark spark-two">✳</span>
</div>
</section>
<section class="home-bottom">
<div><span class="section-kicker">С чего начать</span><h2>Всё просто</h2></div>
<div class="steps-grid">
<article class="step-card"><span class="step-number">01</span><h3>Выберите технику</h3><p>Посмотрите список и характеристики оборудования.</p></article>
<article class="step-card"><span class="step-number">02</span><h3>Укажите время</h3><p>Проверьте, свободно ли оборудование в нужный период.</p></article>
<article class="step-card"><span class="step-number">03</span><h3>Планируйте работу</h3><p>Узнайте стоимость аренды заранее.</p></article>
</div>
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

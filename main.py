from datetime import datetime
from decimal import Decimal, ROUND_CEILING


def is_period_valid(start, end):
    return start < end


def is_equipment_available(is_working, start, end, booked_start, booked_end):
    if not is_period_valid(start, end):
        return False
    if not is_period_valid(booked_start, booked_end):
        return False
    has_overlap = start < booked_end and booked_start < end
    return is_working and not has_overlap


def calculate_cost(start, end, hourly_rate):
    if not is_period_valid(start, end):
        raise ValueError("Конец периода должен быть позже начала.")
    if not hourly_rate.is_finite() or hourly_rate < 0:
        raise ValueError("Тариф должен быть конечным неотрицательным числом.")
    duration_seconds = Decimal(str((end - start).total_seconds()))
    billable_hours = (duration_seconds / Decimal("3600")).to_integral_value(
        rounding=ROUND_CEILING
    )
    return (billable_hours * hourly_rate).quantize(Decimal("0.01"))


def get_booking_status(is_active_user, is_available):
    if not is_active_user:
        return "Отказ: пользователь неактивен."
    if not is_available:
        return "Отказ: оборудование недоступно в выбранный период."
    return "Бронирование подтверждено."


def main():
    user_name = "Иван Петров"
    is_active_user = True
    equipment_name = "Проектор Epson EB-X49"
    is_working = True
    hourly_rate = Decimal("250.00")
    start = datetime.fromisoformat("2026-10-15 12:00")
    end = datetime.fromisoformat("2026-10-15 14:30")
    booked_start = datetime.fromisoformat("2026-10-15 09:00")
    booked_end = datetime.fromisoformat("2026-10-15 12:00")

    print("Сервис бронирования оборудования")
    print(f"Пользователь: {user_name}")
    print(f"Оборудование: {equipment_name}")
    print(f"Период: {start:%d.%m.%Y %H:%M} - {end:%d.%m.%Y %H:%M}")
    print(f"Тариф: {hourly_rate:.2f} руб./час (округление часов вверх)")
    if not is_period_valid(start, end):
        print("Отказ: конец периода должен быть позже начала.")
        return
    is_available = is_equipment_available(
        is_working, start, end, booked_start, booked_end
    )
    print(get_booking_status(is_active_user, is_available))
    if is_active_user and is_available:
        cost = calculate_cost(start, end, hourly_rate)
        print(f"Стоимость: {cost:.2f} руб.")
        print("Бронь сформирована в демонстрационном режиме без сохранения.")


if __name__ == "__main__":
    main()

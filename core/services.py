from typing import TypeVar

from core.models import Booking, Equipment, Period, User

Entity = TypeVar("Entity", User, Equipment, Booking)


def find_by_id(items: list[Entity], entity_id: int) -> Entity:
    for item in items:
        if item.id == entity_id:
            return item
    raise ValueError(f"Объект с ID {entity_id} не найден.")


def next_id(items: list[Entity]) -> int:
    return max((item.id for item in items), default=0) + 1


def search_equipment(
    items: list[Equipment], query: str,
) -> list[Equipment]:
    return [item for item in items if query.casefold() in item.name.casefold()]


def sort_equipment(items: list[Equipment]) -> list[Equipment]:
    return sorted(items, key=lambda item: (item.hourly_rate, item.id))


def is_available(
    equipment: Equipment, period: Period, bookings: list[Booking],
) -> bool:
    return equipment.is_working and not any(
        booking.equipment.id == equipment.id
        and not booking.is_cancelled
        and booking.period.overlaps(period)
        for booking in bookings
    )


def filter_available(
    items: list[Equipment], period: Period, bookings: list[Booking],
) -> list[Equipment]:
    return [item for item in items if is_available(item, period, bookings)]


def create_booking(
    bookings: list[Booking], user: User, equipment: Equipment, period: Period,
) -> Booking:
    if not user.is_active:
        raise ValueError("Пользователь неактивен.")
    if not is_available(equipment, period, bookings):
        raise ValueError("Оборудование недоступно в выбранный период.")
    booking = Booking(next_id(bookings), user, equipment, period)
    bookings.append(booking)
    return booking

import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from models import Booking, Equipment, Period, User
from services import find_by_id


def save_data(
    path: Path, users: list[User], equipment: list[Equipment],
    bookings: list[Booking],
) -> None:
    data = {
        "users": [
            {"id": user.id, "name": user.name, "email": user.email,
             "is_active": user.is_active}
            for user in users
        ],
        "equipment": [
            {"id": item.id, "name": item.name,
             "hourly_rate": str(item.hourly_rate),
             "is_working": item.is_working}
            for item in equipment
        ],
        "bookings": [
            {"id": booking.id, "user_id": booking.user.id,
             "equipment_id": booking.equipment.id,
             "start": booking.period.start.isoformat(),
             "end": booking.period.end.isoformat(),
             "is_cancelled": booking.is_cancelled,
             "hourly_rate": str(booking.hourly_rate)}
            for booking in bookings
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def load_data(
    path: Path,
) -> tuple[list[User], list[Equipment], list[Booking]]:
    if not path.exists():
        return [], [], []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        users = [
            User(row["id"], row["name"], row["email"], row["is_active"])
            for row in data["users"]
        ]
        equipment = [
            Equipment(row["id"], row["name"], Decimal(row["hourly_rate"]),
                      row["is_working"])
            for row in data["equipment"]
        ]
        bookings = [
            Booking(
                row["id"], find_by_id(users, row["user_id"]),
                find_by_id(equipment, row["equipment_id"]),
                Period(datetime.fromisoformat(row["start"]),
                       datetime.fromisoformat(row["end"])),
                row["is_cancelled"], Decimal(row["hourly_rate"]),
            )
            for row in data["bookings"]
        ]
        for collection in (users, equipment, bookings):
            ids = [item.id for item in collection]
            if len(ids) != len(set(ids)):
                raise ValueError("Повторяющиеся ID.")
        for index, booking in enumerate(bookings):
            if booking.is_cancelled:
                continue
            if any(
                other.equipment.id == booking.equipment.id
                and not other.is_cancelled
                and other.period.overlaps(booking.period)
                for other in bookings[:index]
            ):
                raise ValueError("В файле есть пересекающиеся бронирования.")
        return users, equipment, bookings
    except (KeyError, TypeError, ValueError, AttributeError,
            InvalidOperation) as error:
        raise ValueError(f"Некорректный файл данных: {path}") from error

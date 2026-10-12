import json
import subprocess
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from core.models import Booking, Equipment, Period, User
from core.services import (
    create_booking,
    filter_available,
    find_by_id,
    is_available,
    search_equipment,
    sort_equipment,
)
from core.storage import load_data, save_data


@pytest.fixture
def user() -> User:
    return User(1, "Иван", "ivan@example.com")


@pytest.fixture
def equipment() -> Equipment:
    return Equipment(1, "Проектор", Decimal("250.00"))


@pytest.fixture
def period() -> Period:
    return Period(datetime(2026, 10, 15, 12), datetime(2026, 10, 15, 14, 30))


@pytest.mark.parametrize("minutes", [0, -1])
def test_invalid_period(minutes: int) -> None:
    start = datetime(2026, 10, 15, 12)
    with pytest.raises(ValueError):
        Period(start, start + timedelta(minutes=minutes))


@pytest.mark.parametrize("seconds, cost", [
    (1, "250.00"), (7200, "500.00"), (9000, "750.00"),
])
def test_cost(equipment: Equipment, seconds: int, cost: str) -> None:
    start = datetime(2026, 10, 15, 12)
    period = Period(start, start + timedelta(seconds=seconds))
    assert equipment.calculate_cost(period) == Decimal(cost)


@pytest.mark.parametrize("rate", ["-1", "NaN", "Infinity"])
def test_invalid_rate(rate: str) -> None:
    with pytest.raises(ValueError):
        Equipment(1, "Проектор", Decimal(rate))


def test_free_equipment(period: Period) -> None:
    assert Equipment(1, "Проектор", Decimal("0")).calculate_cost(period) == 0


@pytest.mark.parametrize("start, end, expected", [
    (-180, 0, True), (150, 180, True), (0, 150, False),
    (-60, 180, False), (30, 60, False), (-60, 1, False), (149, 180, False),
])
def test_availability(
    user: User, equipment: Equipment, period: Period,
    start: int, end: int, expected: bool,
) -> None:
    other = Period(period.start + timedelta(minutes=start),
                   period.start + timedelta(minutes=end))
    booking = Booking(1, user, equipment, other)
    assert is_available(equipment, period, [booking]) is expected


def test_cancel_releases_equipment(
    user: User, equipment: Equipment, period: Period,
) -> None:
    bookings = []
    first = create_booking(bookings, user, equipment, period)
    with pytest.raises(ValueError):
        create_booking(bookings, user, equipment, period)
    first.cancel()
    first.cancel()
    second = create_booking(bookings, user, equipment, period)
    assert first.status == "Отменено"
    assert second.status == "Подтверждено"
    assert second.id == 2
    assert second.user is user
    assert second.equipment is equipment
    assert second.period is period


def test_inactive_user_and_broken_equipment(
    user: User, equipment: Equipment, period: Period,
) -> None:
    bookings = []
    user.is_active = False
    with pytest.raises(ValueError, match="неактивен"):
        create_booking(bookings, user, equipment, period)
    user.is_active = True
    equipment.is_working = False
    with pytest.raises(ValueError, match="недоступно"):
        create_booking(bookings, user, equipment, period)
    assert bookings == []


def test_other_equipment_is_not_blocked(
    user: User, equipment: Equipment, period: Period,
) -> None:
    other = Equipment(2, "Камера", Decimal("400"))
    bookings = [Booking(1, user, equipment, period)]
    assert is_available(other, period, bookings)
    assert filter_available([equipment, other], period, bookings) == [other]


def test_collections(equipment: Equipment) -> None:
    other = Equipment(2, "Камера", Decimal("400"))
    items = [other, equipment]
    assert search_equipment(items, "ПРОЕК") == [equipment]
    assert sort_equipment(items) == [equipment, other]
    assert find_by_id(items, 1) is equipment
    with pytest.raises(ValueError):
        find_by_id(items, 99)


def test_string_representations(
    user: User, equipment: Equipment, period: Period,
) -> None:
    booking = Booking(1, user, equipment, period)
    assert "Иван" in str(user)
    assert "Проектор" in str(equipment)
    assert "15.10.2026 12:00" in str(period)
    assert "750.00" in str(booking)
    assert "Подтверждено" in str(booking)


def test_roundtrip_and_fixed_rate(
    tmp_path: Path, user: User, equipment: Equipment, period: Period,
) -> None:
    booking = Booking(1, user, equipment, period)
    booking.cancel()
    equipment.hourly_rate = Decimal("999")
    path = tmp_path / "service.json"
    save_data(path, [user], [equipment], [booking])
    users, items, bookings = load_data(path)
    assert bookings[0].user is users[0]
    assert bookings[0].equipment is items[0]
    assert bookings[0].is_cancelled
    assert bookings[0].cost == Decimal("750.00")
    assert bookings[0].period.end == period.end
    assert items[0].hourly_rate == Decimal("999")
    save_data(path, users, items, bookings)
    assert load_data(path)[2][0].cost == Decimal("750.00")


@pytest.mark.parametrize("contents", ["{", "[]", '{}'])
def test_corrupt_file(tmp_path: Path, contents: str) -> None:
    path = tmp_path / "bad.json"
    path.write_text(contents, encoding="utf-8")
    with pytest.raises(ValueError, match="Некорректный файл"):
        load_data(path)
    assert path.read_text(encoding="utf-8") == contents


@pytest.mark.parametrize("fault", ["missing_user", "duplicate_id", "overlap"])
def test_invalid_links_and_duplicates(tmp_path: Path, fault: str) -> None:
    source = Path(__file__).resolve().parents[1] / "data/example.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    if fault == "missing_user":
        data["bookings"][0]["user_id"] = 99
    elif fault == "duplicate_id":
        data["users"].append(data["users"][0])
    else:
        other = dict(data["bookings"][0], id=2)
        data["bookings"].append(other)
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        load_data(path)


def test_missing_file(tmp_path: Path) -> None:
    assert load_data(tmp_path / "missing.json") == ([], [], [])


def test_menu_persistence_and_bad_input(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    path = tmp_path / "service.json"
    actions = (
        "6\nabc\n7\n1\n1\n2026-10-15 12:00\n2026-10-15 14:30\n"
        "9\n2\n0\n"
    )
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(root / "main.py"),
         "--data", str(path)],
        input=actions, text=True, encoding="utf-8", capture_output=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert "Ошибка:" in result.stdout
    assert "750.00" in result.stdout
    assert load_data(path)[2][-1].is_cancelled
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(root / "main.py"),
         "--data", str(path)],
        input="8\n0\n", text=True, encoding="utf-8", capture_output=True,
        timeout=10,
    )
    assert result.returncode == 0
    assert "Отменено" in result.stdout


def test_corrupt_file_stops_program(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    path = tmp_path / "bad.json"
    path.write_text("{broken", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(root / "main.py"),
         "--data", str(path)],
        input="0\n", text=True, encoding="utf-8", capture_output=True,
        timeout=10,
    )
    assert result.returncode == 1
    assert "Не удалось загрузить данные" in result.stdout
    assert path.read_text(encoding="utf-8") == "{broken"


def test_menu_catalog_and_users(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    path = tmp_path / "service.json"
    actions = (
        "1\n2\nПроектор\n3\nМикрофон\n100\n4\n"
        "5\nОлег\noleg@example.com\n"
        "6\n1\n2026-10-15 12:00\n2026-10-15 14:30\n"
        "10\n2026-10-15 12:00\n2026-10-15 14:30\n0\n"
    )
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(root / "main.py"),
         "--data", str(path)],
        input=actions, text=True, encoding="utf-8", capture_output=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert "Ошибка:" not in result.stdout
    assert "Стоимость: 750.00 руб." in result.stdout
    users, equipment, _ = load_data(path)
    assert users[-1].name == "Олег"
    assert equipment[-1].name == "Микрофон"


@pytest.mark.parametrize("entity_id", [0, -1, True])
def test_invalid_ids(entity_id: int) -> None:
    with pytest.raises(ValueError):
        User(entity_id, "Иван", "ivan@example.com")
    with pytest.raises(ValueError):
        Equipment(entity_id, "Проектор", Decimal("250"))

import argparse
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from models import Booking, Equipment, Period, User
from services import (
    create_booking,
    filter_available,
    find_by_id,
    is_available,
    next_id,
    search_equipment,
    sort_equipment,
)
from storage import load_data, save_data
from utils import input_int, input_period

ROOT = Path(__file__).resolve().parent


def show_items(items: list[User] | list[Equipment] | list[Booking]) -> None:
    if not items:
        print("Список пуст.")
    for item in items:
        print(item)


def run_action(
    choice: str, users: list[User], equipment: list[Equipment],
    bookings: list[Booking],
) -> bool:
    if choice == "1":
        show_items(sort_equipment(equipment))
    elif choice == "2":
        show_items(search_equipment(equipment, input("Название: ")))
    elif choice == "3":
        item = Equipment(
            next_id(equipment), input("Название: "),
            Decimal(input("Тариф за час: ")),
        )
        equipment.append(item)
        print(item)
        return True
    elif choice == "4":
        show_items(users)
    elif choice == "5":
        user = User(next_id(users), input("Имя: "), input("Email: "))
        users.append(user)
        print(user)
        return True
    elif choice == "6":
        item = find_by_id(equipment, input_int("ID оборудования: "))
        period = input_period()
        print("Доступно" if is_available(item, period, bookings)
              else "Недоступно")
        print(f"Стоимость: {item.calculate_cost(period):.2f} руб.")
    elif choice == "7":
        user = find_by_id(users, input_int("ID пользователя: "))
        item = find_by_id(equipment, input_int("ID оборудования: "))
        print(create_booking(bookings, user, item, input_period()))
        return True
    elif choice == "8":
        show_items(bookings)
    elif choice == "9":
        booking = find_by_id(bookings, input_int("ID бронирования: "))
        booking.cancel()
        print(booking)
        return True
    elif choice == "10":
        show_items(filter_available(equipment, input_period(), bookings))
    else:
        print("Нет такого пункта меню.")
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Бронирование оборудования")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument(
        "--data", type=Path, default=ROOT / "data/service.json"
    )
    args = parser.parse_args()
    try:
        source = ROOT / "data/example.json"
        if not args.demo and args.data.exists():
            source = args.data
        users, equipment, bookings = load_data(source)
    except (OSError, ValueError) as error:
        print(f"Не удалось загрузить данные: {error}")
        raise SystemExit(1) from error
    
    if args.demo:
        period = Period(datetime(2026, 10, 15, 12),
                        datetime(2026, 10, 15, 14, 30))
        print(create_booking(bookings, users[0], equipment[0], period))
        return
    
    print("Сервис бронирования оборудования")
    while True:
        print(
            "\n1. Оборудование (по цене)\n2. Поиск оборудования"
            "\n3. Добавить оборудование\n4. Пользователи"
            "\n5. Добавить пользователя\n6. Проверить доступность и цену"
            "\n7. Создать бронь\n8. Бронирования\n9. Отменить бронь"
            "\n10. Свободное оборудование на период\n0. Выход"
        )
        try:
            choice = input("Выберите действие: ").strip()
            if choice == "0":
                return
            changed = run_action(choice, users, equipment, bookings)
            if changed:
                try:
                    save_data(args.data, users, equipment, bookings)
                except OSError as error:
                    print(f"Не удалось сохранить данные: {error}")
                    raise SystemExit(1) from error
                print("Данные сохранены.")
        except (ValueError, InvalidOperation) as error:
            print(f"Ошибка: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nВыход.")
            return


if __name__ == "__main__":
    main()

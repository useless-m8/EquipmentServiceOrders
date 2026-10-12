from decimal import Decimal

from models.period import Period


class Equipment:
    def __init__(
        self, equipment_id: int, name: str, hourly_rate: Decimal,
        is_working: bool = True,
    ) -> None:
        if type(equipment_id) is not int or equipment_id <= 0:
            raise ValueError("ID оборудования должен быть положительным.")
        if not name.strip():
            raise ValueError("Название оборудования не может быть пустым.")
        if not hourly_rate.is_finite() or hourly_rate < 0:
            raise ValueError("Тариф должен быть конечным и неотрицательным.")
        if type(is_working) is not bool:
            raise ValueError("Исправность оборудования должна быть bool.")
        self.id = equipment_id
        self.name = name.strip()
        self.hourly_rate = hourly_rate
        self.is_working = is_working

    def calculate_cost(self, period: Period) -> Decimal:
        return (period.billable_hours * self.hourly_rate).quantize(
            Decimal("0.01")
        )

    def __str__(self) -> str:
        status = "исправно" if self.is_working else "неисправно"
        return (
            f"{self.id}. {self.name}, {self.hourly_rate:.2f} руб./час"
            f" ({status})"
        )

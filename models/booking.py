from decimal import Decimal

from models.equipment import Equipment
from models.period import Period
from models.user import User


class Booking:
    def __init__(
        self, booking_id: int, user: User, equipment: Equipment,
        period: Period, is_cancelled: bool = False,
        hourly_rate: Decimal | None = None,
    ) -> None:
        if type(booking_id) is not int or booking_id <= 0:
            raise ValueError("ID бронирования должен быть положительным.")
        if type(is_cancelled) is not bool:
            raise ValueError("Признак отмены должен быть bool.")
        rate = equipment.hourly_rate if hourly_rate is None else hourly_rate
        if not rate.is_finite() or rate < 0:
            raise ValueError("Некорректный тариф бронирования.")
        self.id = booking_id
        self.user = user
        self.equipment = equipment
        self.period = period
        self._is_cancelled = is_cancelled
        self._hourly_rate = rate

    @property
    def is_cancelled(self) -> bool:
        return self._is_cancelled

    @property
    def hourly_rate(self) -> Decimal:
        return self._hourly_rate

    @property
    def cost(self) -> Decimal:
        return (self.period.billable_hours * self.hourly_rate).quantize(
            Decimal("0.01")
        )

    @property
    def status(self) -> str:
        return "Отменено" if self.is_cancelled else "Подтверждено"

    def cancel(self) -> None:
        self._is_cancelled = True

    def __str__(self) -> str:
        return (
            f"{self.id}. {self.user.name}: {self.equipment.name}, "
            f"{self.period}, {self.cost:.2f} руб. ({self.status})"
        )

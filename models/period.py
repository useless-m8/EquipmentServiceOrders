from datetime import datetime
from decimal import Decimal, ROUND_CEILING


class Period:
    def __init__(self, start: datetime, end: datetime) -> None:
        if start.tzinfo is not None or end.tzinfo is not None:
            raise ValueError("Используйте местное время без часового пояса.")
        if start >= end:
            raise ValueError("Конец периода должен быть позже начала.")
        self._start = start
        self._end = end

    @property
    def start(self) -> datetime:
        return self._start

    @property
    def end(self) -> datetime:
        return self._end

    @property
    def billable_hours(self) -> Decimal:
        seconds = Decimal(str((self.end - self.start).total_seconds()))
        return (seconds / Decimal("3600")).to_integral_value(
            rounding=ROUND_CEILING
        )

    def overlaps(self, other: "Period") -> bool:
        return self.start < other.end and other.start < self.end

    def __str__(self) -> str:
        return f"{self.start:%d.%m.%Y %H:%M} - {self.end:%d.%m.%Y %H:%M}"

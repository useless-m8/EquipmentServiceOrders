from datetime import datetime

from models import Period


def input_int(prompt: str) -> int:
    value = int(input(prompt))
    if value <= 0:
        raise ValueError("Введите положительное целое число.")
    return value


def input_period() -> Period:
    start = datetime.fromisoformat(input("Начало (ГГГГ-ММ-ДД ЧЧ:ММ): "))
    end = datetime.fromisoformat(input("Конец (ГГГГ-ММ-ДД ЧЧ:ММ): "))
    return Period(start, end)

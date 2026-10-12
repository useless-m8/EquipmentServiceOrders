import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from main import (
    calculate_cost,
    get_booking_status,
    is_equipment_available,
    is_period_valid,
)


class BookingTests(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2026, 10, 15, 12)
        self.end = datetime(2026, 10, 15, 14, 30)
        self.rate = Decimal("250.00")

    def test_invalid_periods(self):
        self.assertFalse(is_period_valid(self.start, self.start))
        self.assertFalse(is_period_valid(self.end, self.start))
        self.assertTrue(is_period_valid(self.start, self.end))

    def test_adjacent_periods_are_allowed(self):
        self.assertTrue(is_equipment_available(
            True, self.start, self.end,
            self.start - timedelta(hours=3), self.start,
        ))
        self.assertTrue(is_equipment_available(
            True, self.start, self.end,
            self.end, self.end + timedelta(hours=1),
        ))

    def test_overlap_is_rejected(self):
        for booked_start, booked_end in (
            (self.start, self.end),
            (self.start - timedelta(hours=1), self.end + timedelta(hours=1)),
            (self.start + timedelta(minutes=30), self.end),
            (self.start - timedelta(hours=1), self.start + timedelta(minutes=1)),
            (self.end - timedelta(minutes=1), self.end + timedelta(hours=1)),
        ):
            with self.subTest(start=booked_start, end=booked_end):
                self.assertFalse(is_equipment_available(
                    True, self.start, self.end, booked_start, booked_end,
                ))

    def test_broken_equipment_and_invalid_periods(self):
        self.assertFalse(is_equipment_available(
            False, self.start, self.end,
            self.start - timedelta(hours=1), self.start,
        ))
        self.assertFalse(is_equipment_available(
            True, self.end, self.start, self.start, self.end,
        ))
        self.assertFalse(is_equipment_available(
            True, self.start, self.end, self.end, self.start,
        ))

    def test_price_rounds_started_hours_up(self):
        self.assertEqual(calculate_cost(self.start, self.end, self.rate),
                         Decimal("750.00"))
        self.assertEqual(calculate_cost(
            self.start, self.start + timedelta(hours=2), self.rate,
        ), Decimal("500.00"))
        self.assertEqual(calculate_cost(
            self.start, self.start + timedelta(seconds=1), self.rate,
        ), Decimal("250.00"))
        self.assertEqual(calculate_cost(
            self.start, self.end, Decimal("0"),
        ), Decimal("0.00"))

    def test_invalid_cost_inputs(self):
        for rate in (Decimal("-1"), Decimal("NaN"), Decimal("Infinity")):
            with self.subTest(rate=rate), self.assertRaises(ValueError):
                calculate_cost(self.start, self.end, rate)
        with self.assertRaises(ValueError):
            calculate_cost(self.end, self.start, self.rate)

    def test_confirmation_requires_active_user_and_availability(self):
        self.assertEqual(get_booking_status(True, True),
                         "Бронирование подтверждено.")
        self.assertIn("пользователь неактивен", get_booking_status(False, True))
        self.assertIn("пользователь неактивен", get_booking_status(False, False))
        self.assertIn("оборудование недоступно", get_booking_status(True, False))


if __name__ == "__main__":
    unittest.main()

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from core.models import Booking, Equipment, Period, User
from core.storage import save_data


class EquipmentPagesTests(SimpleTestCase):
    def setUp(self) -> None:
        self.user = User(1, "Иван", "ivan@example.com")
        self.equipment = Equipment(1, "Проектор", Decimal("250.00"))
        self.period = Period(datetime(2026, 10, 15, 9),
                             datetime(2026, 10, 15, 12))
        self.booking = Booking(1, self.user, self.equipment, self.period)
        temp_root = Path(__file__).resolve().parents[1] / ".tmp"
        temp_root.mkdir(exist_ok=True)
        directory = TemporaryDirectory(dir=temp_root)
        self.addCleanup(directory.cleanup)
        self.data_file = Path(directory.name) / "service.json"
        settings = override_settings(SERVICE_DATA_FILE=self.data_file)
        settings.enable()
        self.addCleanup(settings.disable)
        save_data(
            self.data_file, [self.user], [self.equipment], [self.booking]
        )

    def test_main_pages(self) -> None:
        for name in ("index", "equipment_list", "booking_list"):
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "<html", html=False)

    def test_detail_pages_show_related_objects(self) -> None:
        response = self.client.get(
            reverse("equipment_detail", args=[self.equipment.id])
        )
        self.assertContains(response, "Проектор")
        response = self.client.get(
            reverse("booking_detail", args=[self.booking.id])
        )
        self.assertContains(response, "Иван")
        self.assertContains(response, "Проектор")
        self.assertContains(response, "750.00")

    def test_equipment_availability_query(self) -> None:
        url = reverse("equipment_detail", args=[self.equipment.id])
        response = self.client.get(url, {
            "start": "2026-10-15T12:00",
            "end": "2026-10-15T13:00",
        })
        self.assertContains(response, "Доступно")
        response = self.client.get(url, {
            "start": "2026-10-15T11:00",
            "end": "2026-10-15T13:00",
        })
        self.assertContains(response, "Занято или неисправно")

    def test_missing_objects_return_404(self) -> None:
        self.assertEqual(self.client.get(
            reverse("equipment_detail", args=[999])
        ).status_code, 404)
        self.assertEqual(self.client.get(
            reverse("booking_detail", args=[999])
        ).status_code, 404)

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_unknown_url_uses_custom_404(self) -> None:
        response = self.client.get("/missing/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response, "404 — страница не найдена", status_code=404
        )

    def test_invalid_period_shows_error(self) -> None:
        url = reverse("equipment_detail", args=[self.equipment.id])
        response = self.client.get(url, {
            "start": "2026-10-15T14:00",
            "end": "2026-10-15T12:00",
        })
        self.assertContains(
            response, "Конец периода должен быть позже начала"
        )

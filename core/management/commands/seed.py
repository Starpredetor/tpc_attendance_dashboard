from django.core.management.base import BaseCommand
from datetime import date
from lectures.models import Batch, Slot
from students.models import Student


class Command(BaseCommand):
    help = "Seed core data: batches, slots, and dummy students"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding core data..."))

        batches = {
            "Batch 1": None,
            "Batch 2": None,
            "Batch 3": None,
            "Batch 4": None,
        }

        for name in batches.keys():
            batch, _ = Batch.objects.get_or_create(name=name)
            batches[name] = batch

        self.stdout.write(self.style.SUCCESS("✓ Batches created"))

        slots_data = {
            "Slot 1": [
                {"start": "2025-12-15", "end": "2025-12-24"},
                {"start": "2026-01-02", "end": "2026-01-17"},
            ],
            "Slot 2": [
                {"start": "2025-12-15", "end": "2025-12-25"},
                {"start": "2026-01-08", "end": "2026-01-17"},
            ],
            "Slot 3": [
                {"start": "2025-12-15", "end": "2025-12-27"},
                {"start": "2026-01-12", "end": "2026-01-17"},
            ],
        }

        slots = {}
        for name, ranges in slots_data.items():
            slot, created = Slot.objects.get_or_create(
                name=name,
                defaults={"date_ranges": ranges},
            )
            if not created:
                slot.date_ranges = ranges
                slot.save()
            slots[name] = slot

        self.stdout.write(self.style.SUCCESS("✓ Slots created with date ranges"))


    

        self.stdout.write(self.style.SUCCESS("Core data seeding completed"))

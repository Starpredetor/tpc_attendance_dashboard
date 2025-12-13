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


        students_data = [
            {
                "full_name": "Aarav Sharma",
                "roll_number": "23CE0001",
                "batch": "Batch 1",
                "slot": "Slot 1",
                "branch": "CE",
                "email": "aarav.sharma@example.com",
                "contact_number": "9999990001",
                "parent_contact_number": "8888880001",
                "parent_email": "parent.aarav@example.com",
            },
            {
                "full_name": "Riya Verma",
                "roll_number": "23IT0002",
                "batch": "Batch 2",
                "slot": "Slot 1",
                "branch": "IT",
                "email": "riya.verma@example.com",
                "contact_number": "9999990002",
                "parent_contact_number": "8888880002",
                "parent_email": "parent.riya@example.com",
            },
            {
                "full_name": "Kunal Mehta",
                "roll_number": "23AD0003",
                "batch": "Batch 4",
                "slot": "Slot 3",
                "branch": "AD",
                "email": "kunal.mehta@example.com",
                "contact_number": "9999990003",
                "parent_contact_number": "8888880003",
                "parent_email": "parent.kunal@example.com",
            },
        ]

        for s in students_data:
            Student.objects.get_or_create(
                roll_number=s["roll_number"],
                defaults={
                    "full_name": s["full_name"],
                    "batch": batches[s["batch"]],
                    "slot": slots[s["slot"]],
                    "branch": s["branch"],
                    "email": s["email"],
                    "contact_number": s["contact_number"],
                    "parent_contact_number": s["parent_contact_number"],
                    "parent_email": s["parent_email"],
                    "is_active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("Core data seeding completed"))

from datetime import date
from django.core.management.base import BaseCommand
from lectures.models import Batch, Slot, Lecture
from accounts.models import User

class Command(BaseCommand):
    help = "Seed fixed lectures for 15th and 16th Dec (hard-coded)"

    def handle(self, *args, **kwargs):
        dates = [
            date(2025, 12, 15),
            date(2025, 12, 16),
        ]

        batch_slot_map = {
            "Batch 1": "Slot 1",
            "Batch 2": "Slot 1",
            "Batch 3": "Slot 2",
            "Batch 4": "Slot 3",
        }

        lecture_types = [
            ("MS", "Morning Session"),
            ("AS", "Afternoon Session"),
        ]

        created = 0
        skipped = 0

        for d in dates:
            for batch_name, slot_name in batch_slot_map.items():
                batch = Batch.objects.get(name=batch_name)
                slot = Slot.objects.get(name=slot_name)
                user = User.objects.get(email="admin@tpc.com")

                for lec_type, lec_label in lecture_types:
                    obj, was_created = Lecture.objects.get_or_create(
                        batch=batch,
                        slot=slot,
                        date=d,
                        lecture_type=lec_type,
                        created_by = user,
                        defaults={
                            "title": f"{lec_label} - {batch_name}",
                        },
                    )

                    if was_created:
                        created += 1
                    else:
                        skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"SEED COMPLETE → Created: {created}, Skipped (already exists): {skipped}"
            )
        )

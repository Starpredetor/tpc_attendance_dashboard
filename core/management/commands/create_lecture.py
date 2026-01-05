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
            date(2025, 12, 17),
            date(2025, 12, 18),
            date(2025, 12, 19),
            date(2025, 12, 20),
            date(2025, 12, 22),

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

        for slot_name in {"Slot 1", "Slot 2", "Slot 3"}:
            if not Slot.objects.filter(name=slot_name).exists():
                self.stdout.write(
                    self.style.ERROR(
                        f"Slot '{slot_name}' does not exist. Run seed slots first."
                    )
                )
                return

        try:
            user = User.objects.get(email="admin@tpc.com")
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("Admin user admin@tpc.com does not exist.")
            )
            return

        for d in dates:
            for batch_name, slot_name in batch_slot_map.items():
                slot = Slot.objects.get(name=slot_name)

                try:
                    batch = Batch.objects.get(name=batch_name, slot=slot)
                except Batch.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Batch '{batch_name}' with slot '{slot_name}' does not exist."
                        )
                    )
                    continue

                for lec_type, lec_label in lecture_types:
                    obj, was_created = Lecture.objects.get_or_create(
                        batch=batch,
                        slot=slot,
                        date=d,
                        lecture_type=lec_type,
                        defaults={
                            "title": f"{lec_label} - {batch_name}",
                            "created_by": user,
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

import csv

from django.core.management.base import BaseCommand
from faker import Faker

from students.models import Student, Branch
from lectures.models import Batch, Slot

fake = Faker()



BATCH_SLOT_MAP = {
    "Batch 1": "Slot 1",
    "Batch 2": "Slot 1",
    "Batch 3": "Slot 2",
    "Batch 4": "Slot 3",
}

REQUIRED_HEADERS = {
    "full_name",
    "roll_number",
    "branch",
    "batch",
}


class Command(BaseCommand):
    help = "Import students from CSV (supports dry-run)"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to CSV file")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate only, no database writes",
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        dry_run = options["dry_run"]

        validated = 0
        errors = []

        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            headers = {
            h.replace("\ufeff", "").strip().lower()
            for h in reader.fieldnames
            }
            if not REQUIRED_HEADERS.issubset(headers):
                self.stderr.write(
                    f"Invalid headers. Found: {reader.fieldnames}"
                )
                return
            

            branch_lookup = {
                b.name.strip().lower(): b
                for b in Branch.objects.all()}
            for row in reader:
                roll = str(row.get("roll_number", "")).strip()
                if not roll:
                    continue

                batch_name = row.get("batch", "").strip()
                branch_raw = (
                    row.get("branch", "")
                    .strip()
                    .strip('"')
                    .strip("'")
                    .lower()
                )

                branch = branch_lookup.get(branch_raw)

                if not branch:
                    errors.append(f"{roll}: Invalid branch '{branch_raw}'")
                    continue

                full_name = row.get("\ufefffull_name", "").strip()

                
                batch = Batch.objects.filter(name=batch_name).first()
                if not batch:
                    errors.append(f"{roll}: Invalid batch '{batch_name}'")
                    continue

                slot_name = BATCH_SLOT_MAP.get(batch_name)
                if not slot_name:
                    errors.append(f"{roll}: No slot mapping for '{batch_name}'")
                    continue

                slot = Slot.objects.filter(name=slot_name).first()
                if not slot:
                    errors.append(f"{roll}: Slot not found '{slot_name}'")
                    continue

                """branch = BRANCH_MAP.get(branch_raw)
                if not branch:
                    errors.append(f"{roll}: Invalid branch '{branch_raw}'")
                    continue"""

                validated += 1
                if roll in Student.objects.values_list("roll_number", flat=True):
                    errors.append(f"{roll}: Duplicate roll number")
                    continue
                if dry_run:
                    print(f"DRY RUN: {full_name} ({roll}) - {batch.name}, {slot.name}, {branch.name}")
                    continue
                try:    
                    Student.objects.create(
                        full_name=full_name,
                        roll_number=roll,
                        branch=branch,
                        batch=batch,
                        slot=slot,
                        email=fake.email(),
                        contact_number=fake.msisdn(),
                        parent_email=fake.email(),
                        parent_contact_number=fake.msisdn(),
                        is_active=True,
                    )
                except Exception as e:
                    errors.append(f"{roll}: Error creating student - {e}")
                    continue

        
        self.stdout.write(
            self.style.SUCCESS(
                f"{'DRY RUN OK' if dry_run else 'IMPORT COMPLETE'} → "
                f"{validated} students validated"
            )
        )

        if errors:
            self.stdout.write(self.style.WARNING("\nWARNINGS:"))
            for e in errors:
                self.stdout.write(f"- {e}")

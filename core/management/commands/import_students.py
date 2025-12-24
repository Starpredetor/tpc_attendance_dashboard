import json
from django.core.management.base import BaseCommand
from students.models import Student, Branch
from lectures.models import Batch
from django.utils.text import slugify
import re


class Command(BaseCommand):
    help = "Import students from JSON (batch-based, no slot)"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        file_path = options["file"]
        dry_run = options["dry_run"]

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        created = 0
        skipped = 0

        flags = {
            "no_email": [],
            "no_parent_email": [],
            "used_alternate_parent_contact": [],
        }

        for _, row in data.items():
            try: 
                roll = row.get("roll_number")
            except AttributeError:
                self.stdout.write(self.style.ERROR(f"Invalid row format: {row}"))
                skipped += 1
                continue
            name = row.get("name")
            branch_name = row.get("branch")
            batch_name = row.get("batch")
            if not re.match(r'^(22|23|24|25)[A-Z]{2}\d{4}$', roll or ""):
                self.stdout.write(self.style.ERROR(f"Invalid roll number '{roll}'"))
                skipped += 1
                continue
            if not roll or not branch_name or not batch_name:
                skipped += 1
                continue

            try:
                branch = Branch.objects.get(name__iexact=branch_name.strip())
            except Branch.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Unknown branch '{branch_name}' for {roll}")
                )
                skipped += 1
                continue

            try:
                batch = Batch.objects.get(name=batch_name.strip())
            except Batch.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Unknown batch '{batch_name}' for {roll}")
                )
                skipped += 1
                continue

            email = row.get("email_id") or None
            contact = row.get("contact") or ""

            parent_email = row.get("parent_email")
            parent_contact = row.get("parent_contact")

            if not parent_email or parent_email.lower() == "na":
                parent_email = row.get("parent_alternate_email")
                flags["no_parent_email"].append(roll)
            if not parent_contact or parent_contact.lower() == "na":
               parent_contact = row.get("parent_alternate_contact")
               flags["used_alternate_parent_contact"].append(roll)


            if not email:
                flags["no_email"].append(roll)

            if not parent_email:
                flags["no_parent_email"].append(roll)

            if dry_run:
                created += 1
                continue

            obj, was_created = Student.objects.get_or_create(
                roll_number=roll,
                defaults={
                    "full_name": name,
                    "branch": branch,
                    "batch": batch,
                    "email": email or f"{slugify(roll)}@example.com",
                    "contact_number": contact,
                    "parent_email": parent_email or "",
                    "parent_contact_number": parent_contact,
                    "is_active": True,
                },
            )

            if was_created:
                created += 1
            else:
                skipped += 1

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"DRY RUN OK → {created} students validated (no DB writes)"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"IMPORTED → {created} students")
            )
            self.stdout.write(
                self.style.WARNING(f"SKIPPED → {skipped} students")
            )

        self.stdout.write("\nFlags summary:")
        self.stdout.write(f"• No email: {len(flags['no_email'])}")
        self.stdout.write(f"• No parent email: {len(flags['no_parent_email'])}")
        self.stdout.write(
            f"• Used alternate parent contact: {len(flags['used_alternate_parent_contact'])}"
        )

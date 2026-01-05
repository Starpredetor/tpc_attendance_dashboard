import random
from datetime import date as date_cls

from django.core.management.base import BaseCommand
from django.utils import timezone

from lectures.models import Lecture
from students.models import Student
from attendance.models import AttendanceRecord


class Command(BaseCommand):
    help = "Mark random attendance for testing (per lecture)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            help="Lecture date (YYYY-MM-DD). Defaults to today",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate only, no DB writes",
        )
        parser.add_argument(
            "--present-ratio",
            type=int,
            default=80,
            help="Percentage of students to mark PRESENT (default: 80)",
        )

    def handle(self, *args, **options):
        date_str = options.get("date")
        dry_run = options["dry_run"]
        present_ratio = options["present_ratio"]

        lecture_date = (
            timezone.datetime.fromisoformat(date_str).date()
            if date_str
            else timezone.localdate()
        )

        self.stdout.write(
            f"{'DRY RUN' if dry_run else 'RUNNING'} → "
            f"Marking attendance for {lecture_date}"
        )

        lectures = Lecture.objects.filter(date=lecture_date)

        if not lectures.exists():
            self.stdout.write(self.style.WARNING("No lectures found for this date"))
            return

        total_created = 0
        total_updated = 0

        for lecture in lectures:
            students = Student.objects.filter(
                batch=lecture.batch,
                slot=lecture.slot,
                is_active=True,
            )

            if not students.exists():
                continue

            student_ids = list(students.values_list("id", flat=True))
            random.shuffle(student_ids)

            present_cutoff = int(len(student_ids) * (present_ratio / 100))
            present_ids = set(student_ids[:present_cutoff])

            self.stdout.write(
                f"Lecture {lecture.id} | "
                f"{lecture.batch.name} | "
                f"{lecture.get_lecture_type_display()} | "
                f"{len(student_ids)} students"
            )

            for student in students:
                status = "P" if student.id in present_ids else "A"

                if dry_run:
                    continue

                obj, created = AttendanceRecord.objects.update_or_create(
                    student=student,
                    lecture=lecture,
                    defaults={
                        "status": status,
                        "marked_by": None,  # system-generated
                    },
                )

                if created:
                    total_created += 1
                else:
                    total_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{'DRY RUN OK' if dry_run else 'DONE'} → "
                f"Created: {total_created}, Updated: {total_updated}"
            )
        )

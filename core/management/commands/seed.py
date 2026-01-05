from django.core.management.base import BaseCommand
from lectures.models import Batch
from students.models import Branch


class Command(BaseCommand):
    help = "Seed core data: slots, batches, and branches"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding core data..."))


        batches = [
            "Batch 1",
            "Batch 2",
            "Batch 3",
            "Batch 4",
        ]

        for batch_name in batches:
            Batch.objects.get_or_create(
                name=batch_name,
            )

        self.stdout.write(self.style.SUCCESS("✓ Batches created"))

        branches = [
            "Computer Engineering",
            "Artificial Intelligence and Data Science",
            "Artificial Intelligence and Machine Learning",
            "Cybersecurity",
            "Information Technology",
            "Computer Science and Business System",
            "Electronics and Computer Engineering",
            "Electronics and Telecommunication Engineering",
            "Electronics Engineering",
        ]

        for name in branches:
            Branch.objects.get_or_create(name=name)

        self.stdout.write(self.style.SUCCESS("✓ Branches created"))

        self.stdout.write(self.style.SUCCESS("Core data seeding completed"))

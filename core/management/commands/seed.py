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
        "full_name": "Mohit Patil",
        "roll_number": "23EC0003",
        "batch": "Batch 1",
        "slot": "Slot 1",
        "branch": "EC",
        "email": "mohit.patil@example.com",
        "contact_number": "9999990003",
        "parent_contact_number": "8888880003",
        "parent_email": "parent.mohit@example.com",
    },
    {
        "full_name": "Sneha Iyer",
        "roll_number": "23AM0004",
        "batch": "Batch 2",
        "slot": "Slot 1",
        "branch": "AM",
        "email": "sneha.iyer@example.com",
        "contact_number": "9999990004",
        "parent_contact_number": "8888880004",
        "parent_email": "parent.sneha@example.com",
    },
    {
        "full_name": "Rahul Deshpande",
        "roll_number": "23CB0005",
        "batch": "Batch 1",
        "slot": "Slot 1",
        "branch": "CB",
        "email": "rahul.deshpande@example.com",
        "contact_number": "9999990005",
        "parent_contact_number": "8888880005",
        "parent_email": "parent.rahul@example.com",
    },

    {
        "full_name": "Ananya Kulkarni",
        "roll_number": "23CE0006",
        "batch": "Batch 2",
        "slot": "Slot 1",
        "branch": "CE",
        "email": "ananya.kulkarni@example.com",
        "contact_number": "9999990006",
        "parent_contact_number": "8888880006",
        "parent_email": "parent.ananya@example.com",
    },
    {
        "full_name": "Vishal Singh",
        "roll_number": "23IT0007",
        "batch": "Batch 3",
        "slot": "Slot 2",
        "branch": "IT",
        "email": "vishal.singh@example.com",
        "contact_number": "9999990007",
        "parent_contact_number": "8888880007",
        "parent_email": "parent.vishal@example.com",
    },
    {
        "full_name": "Pooja Nair",
        "roll_number": "23AD0008",
        "batch": "Batch 3",
        "slot": "Slot 2",
        "branch": "AD",
        "email": "pooja.nair@example.com",
        "contact_number": "9999990008",
        "parent_contact_number": "8888880008",
        "parent_email": "parent.pooja@example.com",
    },
    {
        "full_name": "Siddharth Jain",
        "roll_number": "23EC0009",
        "batch": "Batch 3",
        "slot": "Slot 2",
        "branch": "EC",
        "email": "siddharth.jain@example.com",
        "contact_number": "9999990009",
        "parent_contact_number": "8888880009",
        "parent_email": "parent.siddharth@example.com",
    },
    {
        "full_name": "Neha Gupta",
        "roll_number": "23AM0010",
        "batch": "Batch 3",
        "slot": "Slot 2",
        "branch": "AM",
        "email": "neha.gupta@example.com",
        "contact_number": "9999990010",
        "parent_contact_number": "8888880010",
        "parent_email": "parent.neha@example.com",
    },

    {
        "full_name": "Kunal Mehta",
        "roll_number": "23AD0011",
        "batch": "Batch 4",
        "slot": "Slot 3",
        "branch": "AD",
        "email": "kunal.mehta@example.com",
        "contact_number": "9999990011",
        "parent_contact_number": "8888880011",
        "parent_email": "parent.kunal@example.com",
    },
    {
        "full_name": "Ishaan Malhotra",
        "roll_number": "23CE0012",
        "batch": "Batch 4",
        "slot": "Slot 3",
        "branch": "CE",
        "email": "ishaan.malhotra@example.com",
        "contact_number": "9999990012",
        "parent_contact_number": "8888880012",
        "parent_email": "parent.ishaan@example.com",
    },
    {
        "full_name": "Tanvi Joshi",
        "roll_number": "23IT0013",
        "batch": "Batch 4",
        "slot": "Slot 3",
        "branch": "IT",
        "email": "tanvi.joshi@example.com",
        "contact_number": "9999990013",
        "parent_contact_number": "8888880013",
        "parent_email": "parent.tanvi@example.com",
    },
    {
        "full_name": "Rohit Kulkarni",
        "roll_number": "23EC0014",
        "batch": "Batch 4",
        "slot": "Slot 3",
        "branch": "EC",
        "email": "rohit.kulkarni@example.com",
        "contact_number": "9999990014",
        "parent_contact_number": "8888880014",
        "parent_email": "parent.rohit@example.com",
    },
    {
        "full_name": "Meera Shah",
        "roll_number": "23CB0015",
        "batch": "Batch 4",
        "slot": "Slot 3",
        "branch": "CB",
        "email": "meera.shah@example.com",
        "contact_number": "9999990015",
        "parent_contact_number": "8888880015",
        "parent_email": "parent.meera@example.com",
    },

    {
        "full_name": "Aditya Rao",
        "roll_number": "23AM0016",
        "batch": "Batch 1",
        "slot": "Slot 1",
        "branch": "AM",
        "email": "aditya.rao@example.com",
        "contact_number": "9999990016",
        "parent_contact_number": "8888880016",
        "parent_email": "parent.aditya@example.com",
    },
    {
        "full_name": "Simran Kaur",
        "roll_number": "23IT0017",
        "batch": "Batch 2",
        "slot": "Slot 1",
        "branch": "IT",
        "email": "simran.kaur@example.com",
        "contact_number": "9999990017",
        "parent_contact_number": "8888880017",
        "parent_email": "parent.simran@example.com",
    },
    {
        "full_name": "Yash Thakur",
        "roll_number": "23CE0018",
        "batch": "Batch 3",
        "slot": "Slot 2",
        "branch": "CE",
        "email": "yash.thakur@example.com",
        "contact_number": "9999990018",
        "parent_contact_number": "8888880018",
        "parent_email": "parent.yash@example.com",
    },
    {
        "full_name": "Priya Chavan",
        "roll_number": "23AD0019",
        "batch": "Batch 1",
        "slot": "Slot 1",
        "branch": "AD",
        "email": "priya.chavan@example.com",
        "contact_number": "9999990019",
        "parent_contact_number": "8888880019",
        "parent_email": "parent.priya@example.com",
    },
    {
        "full_name": "Nikhil Bansal",
        "roll_number": "23EC0020",
        "batch": "Batch 2",
        "slot": "Slot 1",
        "branch": "EC",
        "email": "nikhil.bansal@example.com",
        "contact_number": "9999990020",
        "parent_contact_number": "8888880020",
        "parent_email": "parent.nikhil@example.com",
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

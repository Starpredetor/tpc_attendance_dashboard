# attendance/services.py

from datetime import date
from django.utils import timezone
from django.db import transaction

from lectures.models import Lecture
from students.models import Student
from .models import AttendanceRecord, EODAttendanceRun
from auditlog.models import AuditLog
 


ABSENT = "A"
PRESENT = "P"


@transaction.atomic
def mark_absent_for_date(target_date: date | None = None):
    """
    Automatically mark students ABSENT for lectures
    that occurred on target_date but were not marked PRESENT.
    """

    if target_date is None:
        target_date = timezone.localdate()

    lectures = Lecture.objects.filter(date=target_date)

    if not lectures.exists():
        return  
    for lecture in lectures:
        students = Student.objects.filter(
            batch=lecture.batch,
            is_active=True,
        )

        present_student_ids = AttendanceRecord.objects.filter(
            lecture=lecture,
            status=PRESENT,
        ).values_list("student_id", flat=True)
        absent_students = students.exclude(id__in=present_student_ids)
        for student in absent_students:
            AttendanceRecord.objects.get_or_create(
                student=student,
                lecture=lecture,
                defaults={
                    "status": ABSENT,
                },
            )
        print(f"Marked {len(absent_students) or 0} absent for lecture {lecture.id} on {target_date}")
        AuditLog.objects.create(
        action="EOD_ABSENCE_MARK",
        metadata={"date": str(target_date)},
        )
        EODAttendanceRun.objects.create(run_date=target_date)



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

    lectures = Lecture.objects.filter(date=target_date).select_related('batch')

    if not lectures.exists():
        return  
    
    for lecture in lectures:
        students = Student.objects.filter(
            batch=lecture.batch,
            is_active=True,
        ).only('id')

        present_student_ids = set(
            AttendanceRecord.objects.filter(
                lecture=lecture,
                status=PRESENT,
            ).values_list("student_id", flat=True)
        )
        
        absent_students = [s for s in students if s.id not in present_student_ids]
        
        # Use bulk_create for better performance
        absent_records = [
            AttendanceRecord(
                student=student,
                lecture=lecture,
                status=ABSENT,
            )
            for student in absent_students
        ]
        
        AttendanceRecord.objects.bulk_create(
            absent_records,
            ignore_conflicts=True
        )
        
        print(f"Marked {len(absent_records)} absent for lecture {lecture.id} on {target_date}")
    
    # Create audit log once per run
    AuditLog.objects.create(
        action_type="SYSTEM",
        description=f"EOD absence marking completed for {target_date}",
    )
    
    EODAttendanceRun.objects.get_or_create(run_date=target_date)



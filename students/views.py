from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from students.models import Student
from lectures.models import Lecture
from attendance.models import AttendanceRecord


@login_required
def student_profile(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    today = date.today()

    lectures_qs = Lecture.objects.filter(
        batch=student.batch,
        slot=student.slot,
        date__lte=today,
    )

    total_lectures = lectures_qs.count()

    attendance_qs = AttendanceRecord.objects.filter(
        student=student,
        lecture__in=lectures_qs,
    )

    present_count = attendance_qs.filter(status="P").count()

    attendance_percent = 0
    if total_lectures > 0:
        attendance_percent = round((present_count / total_lectures) * 100, 2)

    last_attended_record = (
        attendance_qs.filter(status="P")
        .select_related("lecture")
        .order_by("-lecture__date")
        .first()
    )

    last_attended = None
    if last_attended_record:
        lec = last_attended_record.lecture
        last_attended = f"{lec.date} ({lec.get_lecture_type_display()})"

    recent_lectures = (
        attendance_qs.filter(status="P")
        .select_related("lecture")
        .order_by("-lecture__date")[:5]
    )

    all_attended_lectures = (
    AttendanceRecord.objects
    .filter(student=student, status="P")
    .select_related("lecture")
    .order_by("-lecture__date")
    )

    context = {
        "student": student,
        "attendance_percent": attendance_percent,
        "attended_count": present_count,
        "total_lectures": total_lectures,
        "last_attended": last_attended,
        "recent_lectures": recent_lectures,
        "all_attended_lectures": all_attended_lectures

    }

    return render(
        request,
        "students/profile.html",
        context,
    )


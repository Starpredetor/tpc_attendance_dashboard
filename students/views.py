from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from students.models import Student
from lectures.models import Lecture
from attendance.models import AttendanceRecord
from auditlog.utils import create_audit_log


@login_required
def student_profile(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    today = timezone.localdate()

    lectures_qs = Lecture.objects.filter(
        batch=student.batch,
        date__lte=today,
    )

    if request.method == "POST":
        lecture_ids = request.POST.getlist("lecture_ids")
        status = request.POST.get("status")

        if status not in ("P", "A"):
            messages.error(request, "Please select a valid status.")
            return redirect("student_profile", student_id=student.id)

        if not lecture_ids:
            messages.error(request, "Select at least one lecture to update.")
            return redirect("student_profile", student_id=student.id)

        selected_lectures = lectures_qs.filter(id__in=lecture_ids)
        if not selected_lectures.exists():
            messages.error(request, "No valid lectures selected.")
            return redirect("student_profile", student_id=student.id)

        updated_count = 0
        for lecture in selected_lectures:
            AttendanceRecord.objects.update_or_create(
                student=student,
                lecture=lecture,
                defaults={
                    "status": status,
                    "marked_by": request.user,
                },
            )
            updated_count += 1

        create_audit_log(
            request=request,
            action_type="ATTENDANCE",
            description=(
                f"Updated attendance for {student.roll_number} "
                f"({updated_count} lecture(s)) to {'Present' if status == 'P' else 'Absent'}"
            ),
            target=student,
        )

        messages.success(request, f"Updated {updated_count} lecture(s) to {status}.")
        return redirect("student_profile", student_id=student.id)

    total_lectures = lectures_qs.count()

    attendance_qs = AttendanceRecord.objects.filter(
        student=student,
        lecture__in=lectures_qs,
    )

    present_count = attendance_qs.filter(status="P").count()

    attendance_percent = (
        round((present_count / total_lectures) * 100, 2)
        if total_lectures > 0 else 0
    )
    absent_count = max(total_lectures - present_count, 0)
    absent_percent = (
        round((absent_count / total_lectures) * 100, 2)
        if total_lectures > 0 else 0
    )

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

    attendance_map = {
        rec.lecture_id: rec.status
        for rec in attendance_qs
    }

    lecture_attendance = []
    for lec in lectures_qs.order_by("-date"):
        lecture_attendance.append({
            "lecture": lec,
            "status": attendance_map.get(lec.id, "A"),
        })

    context = {
        "student": student,
        "attendance_percent": attendance_percent,
        "absent_percent": absent_percent,
        "attended_count": present_count,
        "absent_count": absent_count,
        "total_lectures": total_lectures,
        "last_attended": last_attended,
        "recent_lectures": recent_lectures,
        "lecture_attendance": lecture_attendance,
    }

    return render(request, "students/profile.html", context)

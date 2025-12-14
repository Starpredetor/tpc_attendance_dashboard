from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import AttendanceRecord
from lectures.models import Lecture
from django.contrib.auth.decorators import login_required, user_passes_test
from students.models import Student
from django.core.paginator import Paginator
from django.urls import reverse
import re



def is_admin(user):
    return user.is_authenticated and user.role == "ADMIN"
def is_volunteer(user):
    return user.is_authenticated and user.role == "VOLUNTEER"


@login_required
@user_passes_test(is_admin)
def admin_attendance_list(request):
    query = request.GET.get("q", "")
    students = Student.objects.all()

    if query:
        students = students.filter(
            roll_number__icontains=query
        ) | students.filter(
            full_name__icontains=query
        )

    paginator = Paginator(students.order_by("roll_number"), 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "attendance/admin_attendance_list.html",
        {"page_obj": page_obj},
    )



@login_required
def mark_attendance(request):
    today = timezone.localdate()
    
    if request.method == "GET":
        return render(
            request,
            "attendance/volunteer_attendance_view.html",
        )

    roll_number = request.POST.get("roll_number")
    if not re.match(r'^(23|24)[A-Z]{2}\d{4}$', roll_number):
        messages.error(request, "Invalid roll number format. Enter Manually.")
        return redirect("mark_attendance")

    status = request.POST.get("status")
    session_part = request.POST.get("session_part", "BOTH")

    if not roll_number or not status:
        messages.error(request, "Roll number and status are required.")
        return redirect("mark_attendance")

    try:
        student = Student.objects.get(roll_number=roll_number, is_active=True)
    except Student.DoesNotExist:
        messages.error(request, "Invalid roll number. Student not found.")
        return redirect("mark_attendance")

    lectures_qs = Lecture.objects.filter(
        date=today,
        batch=student.batch,
        slot=student.slot,
    )

    if session_part != "BOTH":
        lectures_qs = lectures_qs.filter(lecture_type=session_part)

    if not lectures_qs.exists():
        messages.error(
            request,
            "No matching lectures found for this student today."
        )
        return redirect("mark_attendance")

    marked_sessions = []

    for lecture in lectures_qs:
        AttendanceRecord.objects.update_or_create(
            student=student,
            lecture=lecture,
            defaults={
                "status": status,
                "marked_by": request.user,
            },
        )
        marked_sessions.append(lecture.get_lecture_type_display())

    session_text = " & ".join(sorted(set(marked_sessions)))

    messages.success(
        request,
        f"{student.roll_number} ({student.batch.name}) marked "
        f"{'Present' if status == 'P' else 'Absent'} "
        f"for {session_text} session(s)."
    )

    return redirect("mark_attendance")


@login_required
def mark_absent(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)

    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("manage_lectures")

    all_students = Student.objects.filter(
        batch=lecture.batch,
        slot=lecture.slot,
        is_active=True,
    )

    present_student_ids = AttendanceRecord.objects.filter(
        lecture=lecture,
        status="P",
    ).values_list("student_id", flat=True)

    students_to_mark_absent = all_students.exclude(
        id__in=present_student_ids
    )

    created_count = 0
    updated_count = 0

    for student in students_to_mark_absent:
        obj, created = AttendanceRecord.objects.update_or_create(
            student=student,
            lecture=lecture,
            defaults={
                "status": "A",
                "marked_by": request.user,
            },
        )
        if created:
            created_count += 1
        else:
            updated_count += 1

    messages.success(
        request,
        f"Marked ABSENT for {created_count + updated_count} students "
        f"(Lecture: {lecture.date}, {lecture.batch.name})"
    )

    return redirect("manage_lectures")

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
from auditlog.utils import create_audit_log



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
        return render(request, "attendance/volunteer_attendance_view.html")

    roll_number = request.POST.get("roll_number", "").strip().upper()
    status = request.POST.get("status")
    session_part = request.POST.get("session_part", "BOTH")

    if not roll_number or not status:
        messages.error(request, "Roll number and status are required.")
        return redirect("mark_attendance")

    if not re.match(r'^(22|23|24|25)[A-Z]{2}\d{4}$', roll_number):
        messages.error(request, "Invalid roll number format. Enter manually.")
        return redirect("mark_attendance")

    try:
        student = Student.objects.select_related('batch').get(roll_number=roll_number, is_active=True)
    except Student.DoesNotExist:
        messages.error(request, "Invalid roll number. Student not found.")
        return redirect("mark_attendance")

    lectures_today = Lecture.objects.filter(date=today, batch=student.batch)

    if not lectures_today.exists():
        messages.error(request, "No lectures exist for this student today.")
        return redirect("mark_attendance")

    if session_part == "BOTH":
        for lecture in lectures_today:
            AttendanceRecord.objects.update_or_create(
                student=student,
                lecture=lecture,
                defaults={"status": "P", "marked_by": request.user},
            )
        messages.success(request, f"{student.roll_number} marked Present for BOTH Morning and Afternoon sessions.")
        return redirect("mark_attendance")

    if session_part == "MS":
        ms = lectures_today.filter(lecture_type="MS").first()
        as_ = lectures_today.filter(lecture_type="AS").first()

        if ms:
            AttendanceRecord.objects.update_or_create(
                student=student,
                lecture=ms,
                defaults={"status": "P", "marked_by": request.user},
            )
        if as_:
            AttendanceRecord.objects.update_or_create(
                student=student,
                lecture=as_,
                defaults={"status": "A", "marked_by": request.user},
            )

        messages.success(request, f"{student.roll_number} marked: Morning (Present), Afternoon (Absent)")
        return redirect("mark_attendance")

    if session_part == "AS":
        ms = lectures_today.filter(lecture_type="MS").first()
        as_ = lectures_today.filter(lecture_type="AS").first()

        if as_:
            AttendanceRecord.objects.update_or_create(
                student=student,
                lecture=as_,
                defaults={"status": "P", "marked_by": request.user},
            )
        if ms:
            AttendanceRecord.objects.update_or_create(
                student=student,
                lecture=ms,
                defaults={"status": "A", "marked_by": request.user},
            )

        messages.success(request, f"{student.roll_number} marked: Morning (Absent), Afternoon (Present)")
        return redirect("mark_attendance")


@login_required
def mark_absent(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)

    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("manage_lectures")

    # Get all students for the batch - prefetch to optimize
    all_students = Student.objects.filter(
        batch=lecture.batch,
        is_active=True,
    )

    # Get IDs of students already marked present - use only()
    present_student_ids = AttendanceRecord.objects.filter(
        lecture=lecture,
        status="P",
    ).values_list("student_id", flat=True)

    # Get students to mark absent
    students_to_mark_absent = all_students.exclude(
        id__in=present_student_ids
    )

    # Bulk create for efficiency
    absent_records = []
    for student in students_to_mark_absent:
        absent_records.append(
            AttendanceRecord(
                student=student,
                lecture=lecture,
                status="A",
                marked_by=request.user,
            )
        )
    
    # Use bulk_create with update_conflicts for better performance
    AttendanceRecord.objects.bulk_create(
        absent_records,
        update_conflicts=True,
        update_fields=['status', 'marked_by'],
        unique_fields=['student', 'lecture']
    )

    messages.success(
        request,
        f"Marked ABSENT for {len(absent_records)} students "
        f"(Lecture: {lecture.date}, {lecture.batch.name})"
    )
    create_audit_log(
    request=request,
    action_type="ATTENDANCE",
    description=f"EOD absent marking for {lecture.batch.name} on {lecture.date}",
    target=lecture,
    )

    return redirect("manage_lectures")

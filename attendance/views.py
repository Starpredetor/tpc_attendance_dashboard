from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date
from .models import AttendanceRecord
from lectures.models import Lecture
from django.contrib.auth.decorators import login_required, user_passes_test
from students.models import Student
from django.core.paginator import Paginator

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
            roll_no__icontains=query
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
    today = date.today()

    # Only today's lectures
    todays_lectures = Lecture.objects.filter(date=today)

    if request.method == "POST":
        lecture_id = request.POST.get("lecture")
        roll_no = request.POST.get("roll_no")
        status = request.POST.get("status")

        # ---- Basic validation ----
        if not lecture_id or not roll_no or not status:
            messages.error(request, "All fields are required.")
            return redirect("mark_attendance")

        session = get_object_or_404(Lecture, id=lecture_id, date=today)

        try:
            student = Student.objects.get(roll_no=roll_no)
        except Student.DoesNotExist:
            messages.error(request, "Invalid roll number.")
            return redirect("mark_attendance")

        # ---- Prevent duplicate marking ----
        attendance, created = AttendanceRecord.objects.update_or_create(
            student=student,
            session=session,
            defaults={
                "status": status,
                "marked_by": request.user,
            },
        )

        if created:
            messages.success(
                request,
                f"Attendance marked: {student.roll_no} → {status}"
            )
        else:
            messages.info(
                request,
                f"Attendance updated: {student.roll_no} → {status}"
            )

        return redirect("mark_attendance")

    return render(
        request,
        "attendance/volunteer_attendance_view.html",
        {
            "todays_lectures": todays_lectures,
        },
    )

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date
from .models import AttendanceRecord
from lectures.models import Lecture
from django.contrib.auth.decorators import login_required, user_passes_test
from students.models import Student
from django.core.paginator import Paginator
from django.urls import reverse



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
    today = date.today()

    # Only today's lectures
    todays_lectures = Lecture.objects.filter(date=today)

    # Lecture context (for GET + POST redirect preservation)
    selected_lecture_id = request.GET.get("lecture")

    if request.method == "POST":
        lecture_id = request.POST.get("lecture")
        roll_number = request.POST.get("roll_number")
        status = request.POST.get("status")


        if not lecture_id or not roll_number or not status:
            messages.error(request, "All fields are required.")
            return redirect(f"{reverse('mark_attendance')}?lecture={lecture_id}")


        lecture = get_object_or_404(
            Lecture,
            id=lecture_id,
            date=today,
        )

        try:
            student = Student.objects.get(
                roll_number=roll_number,
                is_active=True,
            )
        except Student.DoesNotExist:
            messages.error(request, "Invalid roll number.")
            return redirect(f"{reverse('mark_attendance')}?lecture={lecture.id}")

        if student.batch != lecture.batch or student.slot != lecture.slot:
            messages.error(
                request,
                "Student does not belong to this lecture's batch or slot. From Batch: "f"{student.batch.name}")
            return redirect(f"{reverse('mark_attendance')}?lecture={lecture.id}")


        attendance, created = AttendanceRecord.objects.update_or_create(
            student=student,
            lecture=lecture,
            defaults={
                "status": status,
                "marked_by": request.user,
            },
        )

        if created:
            messages.success(
                request,
                f"{student.roll_number} marked {status}"
            )
        else:
            messages.info(
                request,
                f"{student.roll_number} updated to {status}"
            )

        return redirect(f"{reverse('mark_attendance')}?lecture={lecture.id}")

    return render(
        request,
        "attendance/volunteer_attendance_view.html",
        {
            "todays_lectures": todays_lectures,
            "selected_lecture_id": selected_lecture_id,
        },
    )


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
        status="PRESENT",
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
                "status": "ABSENT",
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

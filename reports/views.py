from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from students.models import Student
from .services import generate_student_attendance_excel
from .services import generate_lecture_attendance_matrix_excel
from django.shortcuts import render, redirect
from lectures.models import Batch
from lectures.models import Slot
from django.http import HttpRequest
import re
from django.contrib import messages


@login_required
def student_attendance_report(request,):

    if request.method != "GET":
        return render("templates/reports/student_report.html")
    
    roll_number = request.GET.get("roll_number")
    if roll_number is None:
        messages.error(request, "Roll number is required.")
        return redirect("student_report_page")

    if not re.match(r'^(23|24)[A-Z]{2}\d{4}$', roll_number):
        messages.error(request, "Invalid roll number format.")
        return redirect("student_report_page")
    
    student = get_object_or_404(Student, roll_number=roll_number)
    if not student:
        messages.error(request, "Student does not exist.")
        return redirect("student_report_page")

    return generate_student_attendance_excel(student)

@login_required
def lecture_attendance_report(request: HttpRequest):
    if request.method == "POST":
        batch_ids = request.POST.getlist("batches")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        slot_id = request.POST.get("slot")

        batches = Batch.objects.filter(id__in=batch_ids)
        slot = Slot.objects.get(id=slot_id) if slot_id else None

        return generate_lecture_attendance_matrix_excel(
            batches=batches,
            start_date=start_date,
            end_date=end_date,
        )

    return render(request, "reports/lecture_report_form.html")

@login_required
def reports_index(request):
    return render(request, "reports/reports.html")


@login_required
def student_report_page(request):
    return render(request, "reports/student_report.html")


@login_required
def lecture_report_page(request):
    return render(
        request,
        "reports/lecture_report.html",
        {
            "batches": Batch.objects.all(),
            "slots": Slot.objects.all(),
        },
    )

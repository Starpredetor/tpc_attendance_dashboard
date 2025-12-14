from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from attendance.models import AttendanceRecord
from django.utils import timezone

from .models import Lecture, Slot, Batch

@login_required
def manage_lectures(request):
    lectures = Lecture.objects.all().order_by("-date", "lecture_type")
    slots = Slot.objects.all()
    batches = Batch.objects.all()

    if request.method == "POST":
        try:
            Lecture.objects.create(
                date=request.POST["date"],
                slot_id=request.POST["slot"],
                batch_id=request.POST["batch"],
                title=request.POST.get("title"),
                lecture_type=request.POST["lecture_type"],
                created_by=request.user,
            )
            return redirect("manage_lectures")
        except Exception as e:
            if "unique constraint" in str(e):
                messages.error(request, "Lecture already exists.")
            else:
                messages.error(request, "Error creating lecture.")

    return render(
        request,
        "lectures/manage_lectures.html",
        {
            "lectures": lectures,
            "todays_date": timezone.localdate(),
            "slots": slots,
            "batches": batches,
        },
    )

@login_required
def create_lecture(request):
    try:
        if request.method == "POST":
            Lecture.objects.create(
                date=request.POST["date"],
                slot_id=request.POST["slot"],
                batch_id=request.POST["batch"],
                title=request.POST.get("title"),
                lecture_type=request.POST["lecture_type"],
                created_by=request.user,
            )
            messages.success(request, "Lecture created successfully.")
            return redirect("manage_lectures")
    except Exception as e:
        if "unique constraint" in str(e):
            messages.error(request, "Lecture already exists.")
            return redirect("manage_lectures")
        else:
            messages.error(request, "Error creating lecture.") 
            return redirect("manage_lectures")



@login_required
def edit_lecture(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)

    if request.method == "POST":
        lecture.date = request.POST.get("date")
        lecture.slot_id = request.POST.get("slot")
        lecture.batch_id = request.POST.get("batch")
        lecture.lecture_type = request.POST.get("lecture_type")
        lecture.title = request.POST.get("title", "")

        lecture.save()
        messages.success(request, "Lecture updated successfully.")
        return redirect("manage_lectures",)

    return render(
        request,
        "lectures/edit_lecture.html",
        {
            "lecture": lecture,
        },
    )

@login_required
def delete_lecture(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)

    if request.method != "POST":
        messages.error(request, "Invalid request.")
        return redirect("manage_lectures")

    AttendanceRecord.objects.filter(lecture=lecture).delete()
    lecture.delete()

    messages.success(
        request,
        "Lecture and all related attendance records deleted successfully."
    )

    return redirect("manage_lectures")

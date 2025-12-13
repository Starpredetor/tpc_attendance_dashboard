from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Lecture, Slot, Batch

@login_required
def manage_lectures(request):
    lectures = Lecture.objects.all().order_by("date")
    slots = Slot.objects.all()
    batches = Batch.objects.all()

    if request.method == "POST":
        Lecture.objects.create(
            date=request.POST["date"],
            slot_id=request.POST["slot"],
            batch_id=request.POST["batch"],
            title=request.POST.get("title"),
            lecture_type=request.POST["lecture_type"],
            created_by=request.user,
        )
        return redirect("manage_lectures")

    return render(
        request,
        "lectures/manage_lectures.html",
        {
            "lectures": lectures,
            "slots": slots,
            "batches": batches,
        },
    )

from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from lectures.models import Lecture
from attendance.models import AttendanceRecord
from notifications.models import NotificationLog
from notifications.utils import send_absent_emails
from auditlog.utils import create_audit_log


@login_required
def notifications_view(request):
    selected_date = request.GET.get("date")
    if selected_date:
        selected_date = date.fromisoformat(selected_date)
    else:
        selected_date = timezone.localdate()

    lectures = Lecture.objects.filter(date=selected_date)

    sent_lecture_ids = set(
        NotificationLog.objects.filter(date=selected_date)
        .values_list("lecture_id", flat=True)
    )

    if request.method == "POST":
        lecture_ids = request.POST.getlist("lectures")

        for lecture in lectures.filter(id__in=lecture_ids):
            absent_records = AttendanceRecord.objects.filter(
                lecture=lecture,
                status="A",
            ).select_related("student")

            send_absent_emails(absent_records, lecture, selected_date)

            NotificationLog.objects.create(
                lecture=lecture,
                date=selected_date,
                sent_by=request.user,
            )
        create_audit_log(
    request=request,
    action_type="SYSTEM",
    description=f"Absentee notification sent for {date}",
)

        messages.success(request, "Notifications sent successfully.")
        return redirect("notifications")

    for lec in lectures:
        lec.notification_sent = lec.id in sent_lecture_ids

    return render(
        request,
        "notifications/notifications.html",
        {
            "lectures": lectures,
            "selected_date": selected_date,
            "already_sent": bool(sent_lecture_ids),
        },
    )

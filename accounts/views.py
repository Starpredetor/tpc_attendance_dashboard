from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date
from students.models import Student
from lectures.models import Lecture
from attendance.models import AttendanceRecord
from auditlog.models import AuditLog
from django.utils import timezone
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy



today = timezone.localdate()

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)

            if user.role == "ADMIN":
                return redirect("admin_dashboard")
            elif user.role == "VOLUNTEER":
                return redirect("volunteer_dashboard")

        messages.error(request, "Invalid credentials")

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "dashboards/change_password.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        if response:
            messages.success(self.request, "Password changed successfully.")
        else:
            messages.error(self.request, "Failed to change password.")
        return response



@login_required
def admin_dashboard(request):

    total_students = Student.objects.filter(is_active=True).count()

    todays_lectures = Lecture.objects.filter(date=today).select_related("batch")


    total_expected_today = 0
    total_present_today = 0

    for lecture in todays_lectures:
        students_qs = Student.objects.filter(
            batch=lecture.batch,
            slot=lecture.slot,
            is_active=True,
        )

        total_expected_today += students_qs.count()

        total_present_today += AttendanceRecord.objects.filter(
            lecture=lecture,
            status="P",
        ).count()

    if total_expected_today > 0:
        today_present_percent = round(
            (total_present_today / total_expected_today) * 100, 2
        )
    else:
        today_present_percent = 0

    critical_defaulters = []

    students = Student.objects.filter(is_active=True).select_related("batch", "slot")

    for student in students:
        total_lectures = Lecture.objects.filter(
            batch=student.batch,
            slot=student.slot,
            date__lte=today,
        ).count()

        if total_lectures == 0:
            continue

        present_count = AttendanceRecord.objects.filter(
            student=student,
            status="P",
            lecture__date__lte=today,
        ).count()

        attendance_percent = round((present_count / total_lectures) * 100, 2)

        if attendance_percent < 50:  # Chanagble value 
            critical_defaulters.append({
                "id": student.id,
                "roll_no": student.roll_number,
                "full_name": student.full_name,
                "attendance_percent": attendance_percent,
            })

    # Limit to top 5 worst defaulters
    critical_defaulters = sorted(
        critical_defaulters,
        key=lambda x: x["attendance_percent"]
    )[:5]


    recent_audits = (
        AuditLog.objects
        .select_related("user")
        .order_by("-timestamp")[:10]
    )


    return render(
        request,
        "dashboards/admin_dashboard.html",
        {
            "total_students": total_students,
            "today_present_percent": today_present_percent,
            "critical_defaulters": critical_defaulters,
            "recent_audits": recent_audits,
        },
    )



@login_required
def volunteer_dashboard(request):
    if request.user.role != "VOLUNTEER":
        return redirect("login")
    
    total_students = Student.objects.filter(is_active=True).count()

    todays_lectures = Lecture.objects.filter(date=today).select_related("batch")


    total_expected_today = 0
    total_present_today = 0

    for lecture in todays_lectures:
        students_qs = Student.objects.filter(
            batch=lecture.batch,
            slot=lecture.slot,
            is_active=True,
        )

        total_expected_today += students_qs.count()

        total_present_today += AttendanceRecord.objects.filter(
            lecture=lecture,
            status="P",
        ).count()

    if total_expected_today > 0:
        today_present_percent = round(
            (total_present_today / total_expected_today) * 100, 2
        )
    else:
        today_present_percent = 0


    students = Student.objects.filter(is_active=True).select_related("batch", "slot")

    for student in students:
        total_lectures = Lecture.objects.filter(
            batch=student.batch,
            slot=student.slot,
            date__lte=today,
        ).count()

        if total_lectures == 0:
            continue

        present_count = AttendanceRecord.objects.filter(
            student=student,
            status="P",
            lecture__date__lte=today,
        ).count()

        attendance_percent = round((present_count / total_lectures) * 100, 2)


    return render(
        request,
        "dashboards/volunteer_dashboard.html",
        {
            "total_students": total_students,
            "today_present_percent": today_present_percent,
        },
    )

    return render(request, "dashboards/volunteer_dashboard.html")

@login_required
def dashboard_redirect(request):
    if request.user.role == "ADMIN":
        return redirect("admin_dashboard")
    elif request.user.role == "VOLUNTEER":
        return redirect("volunteer_dashboard")
    return redirect("login")

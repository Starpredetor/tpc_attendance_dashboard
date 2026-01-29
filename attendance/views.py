from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import AttendanceRecord
from lectures.models import Lecture, Batch
from django.contrib.auth.decorators import login_required, user_passes_test
from students.models import Student, Branch
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q, Count
from urllib.parse import urlencode
from datetime import datetime, timedelta
import re
from auditlog.utils import create_audit_log



def is_admin(user):
    return user.is_authenticated and user.role == "ADMIN"
def is_volunteer(user):
    return user.is_authenticated and user.role == "VOLUNTEER"


@login_required
@user_passes_test(is_admin)
def admin_attendance_list(request):
    query = request.GET.get("q", "").strip()
    branch_id = request.GET.get("branch")
    batch_id = request.GET.get("batch")
    active_only = request.GET.get("active", "1") == "1"

    students = Student.objects.all()

    if active_only:
        students = students.filter(is_active=True)

    if query:
        students = students.filter(Q(roll_number__icontains=query) | Q(full_name__icontains=query))

    if branch_id:
        students = students.filter(branch_id=branch_id)

    if batch_id:
        students = students.filter(batch_id=batch_id)

    paginator = Paginator(students.order_by("roll_number"), 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "attendance/admin_attendance_list.html",
        {
            "page_obj": page_obj,
            "branches": Branch.objects.all(),
            "batches": Batch.objects.all(),
            "selected_branch": branch_id,
            "selected_batch": batch_id,
            "active_only": active_only,
            "q": query,
        },
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


@login_required
@user_passes_test(is_admin)
def batch_analysis_index(request):
    return render(
        request,
        "attendance/batch_analysis_index.html",
        {"batches": Batch.objects.all()},
    )


@login_required
@user_passes_test(is_admin)
def batch_attendance_analysis(request, batch_id: int):
    batch = get_object_or_404(Batch, id=batch_id)

    # Student filters
    query = request.GET.get("q", "").strip()
    branch_id = request.GET.get("branch")
    active_only = request.GET.get("active", "1") == "1"

    # Date range: default to 15 Dec 2025 - today
    try:
        start_str = request.GET.get("start_date")
        end_str = request.GET.get("end_date")
        if start_str and end_str:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        else:
            end_date = timezone.localdate()
            start_date = datetime.strptime("2025-12-15", "%Y-%m-%d").date()
    except Exception:
        end_date = timezone.localdate()
        start_date = datetime.strptime("2025-12-15", "%Y-%m-%d").date()

    # Lectures for the batch in range
    lectures = Lecture.objects.filter(batch=batch, date__range=(start_date, end_date)).order_by("date", "lecture_type")
    total_sessions = lectures.count()

    students = Student.objects.filter(batch=batch)
    if active_only:
        students = students.filter(is_active=True)
    if branch_id:
        students = students.filter(branch_id=branch_id)
    if query:
        students = students.filter(Q(roll_number__icontains=query) | Q(full_name__icontains=query))
    students = students.order_by("roll_number")

    base_students = Student.objects.filter(batch=batch)
    if active_only:
        base_students = base_students.filter(is_active=True)

    # Present counts per student
    present_qs = AttendanceRecord.objects.filter(
        lecture__in=lectures,
        status="P",
    ).values("student_id")

    present_by_student = {}
    for row in present_qs:
        sid = row["student_id"]
        present_by_student[sid] = present_by_student.get(sid, 0) + 1

    # Absent recorded counts per student (ACTUAL absences marked as 'A')
    absent_qs = AttendanceRecord.objects.filter(
        lecture__in=lectures,
        status="A",
    ).values("student_id")
    absent_by_student = {}
    for row in absent_qs:
        sid = row["student_id"]
        absent_by_student[sid] = absent_by_student.get(sid, 0) + 1

    # Build per-student data
    percent_values = []
    present_total = 0
    absent_total_recorded = 0

    student_data = []
    for s in students:
        p = present_by_student.get(s.id, 0)
        a = absent_by_student.get(s.id, 0)
        present_total += p
        absent_total_recorded += a
        pct = round((p / total_sessions) * 100, 2) if total_sessions > 0 else 0
        percent_values.append(pct)
        student_data.append({
            "id": s.id,
            "roll_number": s.roll_number,
            "name": s.full_name,
            "branch": s.branch.name if s.branch else "",
            "is_active": s.is_active,
            "present": p,
            "absent": a,
            "percent": pct,
        })

    # Missing records considered absent for aggregate
    potential_records = students.count() * total_sessions
    missing_records = max(potential_records - (present_total + absent_total_recorded), 0)
    absent_total = absent_total_recorded + missing_records

    # Defaulters: top 5 by actual absent count (only marked 'A')
    defaulters = sorted(
        [s for s in student_data if s["absent"] > 0],
        key=lambda x: x["absent"],
        reverse=True
    )[:5]

    paginator = Paginator(student_data, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    params = request.GET.copy()
    if "page" in params:
        del params["page"]
    filter_query = params.urlencode()

    # Day-wise attendance percentage
    dates_in_range = sorted(set(lec.date for lec in lectures))
    daily_labels = [d.strftime("%d %b") for d in dates_in_range]
    daily_percentages = []

    for d in dates_in_range:
        day_lectures = [lec for lec in lectures if lec.date == d]
        day_session_count = len(day_lectures)
        if day_session_count == 0:
            daily_percentages.append(0)
            continue
        # Count present for this day
        day_present = AttendanceRecord.objects.filter(
            lecture__in=day_lectures,
            status="P"
        ).count()
        expected = students.count() * day_session_count
        day_pct = round((day_present / expected) * 100, 2) if expected > 0 else 0
        daily_percentages.append(day_pct)

    # Overall attendance rate
    attendance_rate = 0
    denominator = students.count() * total_sessions
    if denominator > 0:
        attendance_rate = round((present_total / denominator) * 100, 2)

    branch_counts = (
        base_students
        .values("branch__name")
        .annotate(count=Count("id"))
        .order_by("branch__name")
    )
    branch_stats = []
    for row in branch_counts:
        branch_name = row["branch__name"] or "Unknown"
        if row["branch__name"] is None:
            branch_students = base_students.filter(branch__isnull=True)
        else:
            branch_students = base_students.filter(branch__name=row["branch__name"])

        branch_present = AttendanceRecord.objects.filter(
            lecture__in=lectures,
            student__in=branch_students,
            status="P",
        ).count()
        branch_denominator = branch_students.count() * total_sessions
        branch_attendance_rate = round((branch_present / branch_denominator) * 100, 2) if branch_denominator > 0 else 0

        branch_stats.append({
            "name": branch_name,
            "count": row["count"],
            "attendance_rate": branch_attendance_rate,
        })

    top_branch_by_count = max(branch_stats, key=lambda x: x["count"], default=None)
    top_branch_by_attendance = max(branch_stats, key=lambda x: x["attendance_rate"], default=None)

    context = {
        "batch": batch,
        "start_date": start_date,
        "end_date": end_date,
        "present_total": present_total,
        "absent_total": absent_total,
        "attendance_rate": attendance_rate,
        "total_sessions": total_sessions,
        "students_count": students.count(),
        "defaulters": defaulters,
        "daily_labels": daily_labels,
        "daily_percentages": daily_percentages,
        "page_obj": page_obj,
        "branches": Branch.objects.all(),
        "selected_branch": branch_id,
        "active_only": active_only,
        "q": query,
        "filter_query": filter_query,
        "branch_stats": branch_stats,
        "top_branch_by_count": top_branch_by_count,
        "top_branch_by_attendance": top_branch_by_attendance,
    }

    return render(request, "attendance/batch_analysis.html", context)

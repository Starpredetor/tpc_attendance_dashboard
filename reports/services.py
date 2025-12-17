from openpyxl import Workbook
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from collections import defaultdict

from lectures.models import Lecture
from students.models import Student
from attendance.models import AttendanceRecord

from django.utils import timezone

def make_naive(dt):
    return timezone.make_naive(dt) if timezone.is_aware(dt) else dt

PRESENT_FILL = PatternFill(
    start_color="C6EFCE", end_color="C6EFCE", fill_type="solid"
)
ABSENT_FILL = PatternFill(
    start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"
)


def generate_student_attendance_excel(student):
    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance"

    headers = [
        "Lecture Date",
        "Session",
        "Batch",
        "Slot",
        "Lecture Title",
        "Status",
        "Marked At",
        "Last Updated",
    ]

    ws.append(headers)

    records = (
        AttendanceRecord.objects
        .filter(student=student)
        .select_related("lecture", "lecture__batch", "lecture__slot")
        .order_by("lecture__date", "lecture__lecture_type")
    )

    for record in records:
        lecture = record.lecture
        session_name = lecture.get_lecture_type_display()

        ws.append([
            lecture.date,
            session_name,
            lecture.batch.name,
            lecture.slot.name,
            lecture.title or "-",
            "Present" if record.status == "P" else "Absent",
            make_naive(record.marked_at,),
            make_naive(record.updated_at) if hasattr(record, "updated_at") else make_naive(record.marked_at),
        ])

        status_cell = ws.cell(row=ws.max_row, column=6)
        status_cell.fill = (
            PRESENT_FILL if record.status == "P" else ABSENT_FILL
        )

    ws.freeze_panes = "A2"

    for col in range(1, ws.max_column + 1):
        ws.column_dimensions[get_column_letter(col)].width = 20

    safe_name = student.full_name.replace(" ", "_")

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{safe_name}_Attendance_Report.xlsx"'
    )

    wb.save(response)
    return response

def generate_lecture_attendance_matrix_excel(batches, start_date, end_date):
    wb = Workbook()
    wb.remove(wb.active)

    for batch in batches:
        ws = wb.create_sheet(title=batch.name[:31])

        lectures = (
            Lecture.objects
            .filter(batch=batch, date__range=(start_date, end_date))
            .order_by("date", "lecture_type")
        )

        if not lectures.exists():
            continue

        lecture_map = defaultdict(dict)
        for lec in lectures:
            lecture_map[lec.date][lec.lecture_type] = lec

        dates = sorted(lecture_map.keys())

        students = (
            Student.objects
            .filter(batch=batch, is_active=True)
            .order_by("roll_number")
        )

        fixed_headers = [
            "Roll No",
            "Name",
            "Branch",
            "Slot",
            "Attendance %",
        ]

        # ----- HEADER ROWS -----
        ws.append(fixed_headers)

        col = len(fixed_headers) + 1
        for d in dates:
            ws.merge_cells(
                start_row=1,
                start_column=col,
                end_row=1,
                end_column=col + 1,
            )
            ws.cell(row=1, column=col).value = d.strftime("%d-%b-%Y")
            ws.cell(row=2, column=col).value = "Morning"
            ws.cell(row=2, column=col + 1).value = "Afternoon"
            col += 2

        ws.freeze_panes = "F3"

        attendance_lookup = {
            (r.student_id, r.lecture_id): r.status
            for r in AttendanceRecord.objects.filter(
                lecture__batch=batch,
                lecture__date__range=(start_date, end_date)
            )
        }

        row = 3
        for student in students:
            ws.append([
                student.roll_number,
                student.full_name,
                student.branch.name,
                student.slot.name,
                "",
            ])

            present_count = 0
            total_sessions = 0

            col = len(fixed_headers) + 1
            for d in dates:
                for session in ["MS", "AS"]:
                    lec = lecture_map[d].get(session)
                    cell = ws.cell(row=row, column=col)

                    if lec:
                        status = attendance_lookup.get(
                            (student.id, lec.id), "A"
                        )
                        cell.value = status
                        cell.fill = PRESENT_FILL if status == "P" else ABSENT_FILL

                        total_sessions += 1
                        if status == "P":
                            present_count += 1
                    else:
                        cell.value = "-"

                    col += 1

            percentage = 0
            if total_sessions > 0:
                percentage = round((present_count / total_sessions) * 100, 2)

            percent_cell = ws.cell(row=row, column=5)
            percent_cell.value = percentage

            row += 1

        for i in range(1, ws.max_column + 1):
            ws.column_dimensions[get_column_letter(i)].width = 18

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    batch_names = ", ".join(batch.name for batch in batches)

    response["Content-Disposition"] = (
    f'attachment; filename="{start_date}_to_{end_date}_{batch_names}_Attendance_Report.xlsx"'
    )


    wb.save(response)
    return response

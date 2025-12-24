from django.conf import settings
from django.core.mail import send_mail


def send_absent_emails(absent_records, lecture, date):
    subject = f"Attendance Alert – {lecture.batch.name} – {date}"
    TEMP_MAIL = 'example@exmaple.com'
    for record in absent_records:
        student = record.student
        if not student.parent_email:
            continue

        message = (
            f"Dear Parent,\n\n"
            f"Your ward {student.full_name} ({student.roll_number}) "
            f"was marked ABSENT for the {lecture.get_lecture_type_display()} "
            f"session on {date}.\n\n"
            f"Training & Placement Cell"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [TEMP_MAIL],
            fail_silently=True,
        )

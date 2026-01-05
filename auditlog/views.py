# auditlog/views.py
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from .models import AuditLog
from accounts.models import User


@login_required
def audit_log_list(request):
    logs = AuditLog.objects.select_related("actor").all()

    q = request.GET.get("q")
    action = request.GET.get("action")
    user = request.GET.get("user")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if q:
        logs = logs.filter(
            Q(description__icontains=q)
            | Q(target_type__icontains=q)
            | Q(actor__email__icontains=q)
        )

    if action:
        logs = logs.filter(action_type=action)

    if user:
        logs = logs.filter(actor_id=user)

    if start_date:
        logs = logs.filter(timestamp__date__gte=start_date)

    if end_date:
        logs = logs.filter(timestamp__date__lte=end_date)

    context = {
        "logs": logs[:500],  # hard cap for sanity
        "actions": AuditLog.ACTION_CHOICES,
        "users": User.objects.all(),
    }

    return render(request, "auditlog/auditlog.html", context)

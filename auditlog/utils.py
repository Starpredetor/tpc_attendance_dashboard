from auditlog.models import AuditLog

def create_audit_log(
    *,
    request=None,
    actor=None,
    action_type,
    description,
    target=None,
):
    AuditLog.objects.create(
        actor=actor if actor else getattr(request, "user", None),
        action_type=action_type,
        description=description,
        target_type=target.__class__.__name__ if target else None,
        target_id=target.id if target else None,
        ip_address=(
            request.META.get("REMOTE_ADDR")
            if request else None
        ),
    )

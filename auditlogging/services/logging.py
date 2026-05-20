from auditlogging.models import ActivityLog


def log_action(actor,action,message,target_user=None):
    ActivityLog.objects.create(
        actor=actor,
        action=action,
        message=message,
        target_user=target_user
    )
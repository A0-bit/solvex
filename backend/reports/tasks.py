"""
Celery async tasks for the reports app.
"""
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_supervisor_new_report(self, report_id: int):
    """Email the supervisor when a new report lands in their area."""
    try:
        from reports.models import Report

        report = Report.objects.select_related("area__supervisor").get(id=report_id)
        if report.area and report.area.supervisor:
            supervisor = report.area.supervisor
            send_mail(
                subject=f"[GarbageMS] New report in {report.area.name}",
                message=(
                    f"Hello {supervisor.get_full_name() or supervisor.username},\n\n"
                    f"A new garbage report has been submitted in your area.\n\n"
                    f"Report #{report.id}: {report.title}\n"
                    f"Location: ({report.latitude}, {report.longitude})\n"
                    f"Status: {report.status}\n\n"
                    "Please log in to review and assign a cleaner."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[supervisor.email],
                fail_silently=True,
            )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_user_status_change(self, report_id: int, new_status: str):
    """Email the reporter when their report status changes."""
    try:
        from reports.models import Report

        report = Report.objects.select_related("reporter").get(id=report_id)
        reporter = report.reporter
        send_mail(
            subject=f"[GarbageMS] Your report #{report.id} has been updated",
            message=(
                f"Hello {reporter.get_full_name() or reporter.username},\n\n"
                f"Your garbage report '{report.title}' (#{report.id}) "
                f"has been updated to status: {new_status.upper().replace('_', ' ')}.\n\n"
                "Thank you for helping keep your community clean."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reporter.email],
            fail_silently=True,
        )
    except Exception as exc:
        raise self.retry(exc=exc)

from celery import shared_task

from forecasts.utils import report_utils


@shared_task(bind=True)
def generate_report(self, user_id, data):
    """Generate report for the given data, and save it to the database."""
    task_id = self.request.id

    report = report_utils.get_existing_report(user_id, data)
    if report:
        report.task_id = task_id
        report.save()
        return

    result, errors = report_utils.generate_report_content(data)

    report_utils.save_report_to_database(
        user_id,
        task_id,
        data,
        result,
        errors,
    )

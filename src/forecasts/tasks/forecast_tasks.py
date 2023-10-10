import datetime

from celery import shared_task

from forecasts.utils import report_utils


@shared_task(bind=True)
def generate_report(self, user_id, data, report_content):
    """Generate report for the given data, and save it to the database."""
    content_types = {
        "forecast": report_utils.generate_forecast_report,
        "statistics": report_utils.generate_statistics_report,
    }

    task_id = self.request.id

    report = report_utils.get_existing_report(user_id, data)
    if report:
        report.task_id = task_id
        report.save()
        return

    if generator := content_types.get(report_content, None):
        file_name = generate_name(report_content, data)
        result, errors = report_utils.generate_report_content(
            data,
            generator,
            file_name,
        )

        report_utils.save_report_to_database(
            user_id,
            task_id,
            data,
            result,
            errors,
        )
    raise KeyError(
        f'Report content "{report_content}" does not exists',
    )


def generate_name(report_content, data):
    """Generate report file name."""
    from_date = data.get("from_date", None)
    to_date = data.get("to_date", None)
    if from_date and to_date:
        return f"{report_content}_report_between_{from_date}_{to_date}.xlsx"
    return f"{report_content}_report_on_{datetime.date.today()}.xlsx"

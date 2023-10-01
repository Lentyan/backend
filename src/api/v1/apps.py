from django.apps import AppConfig


class V1Config(AppConfig):
    """V1 api app configs."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "api.v1"

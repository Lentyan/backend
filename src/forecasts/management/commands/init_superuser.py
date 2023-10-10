import os

from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    """Create superuser command."""

    def handle(self, *args, **options):
        """Command handler."""
        if User.objects.count() == 0:
            admin = User.objects.create_superuser(
                email=os.getenv("DJANGO_SUPERUSER_EMAIL"),
                password=os.getenv("DJANGO_SUPERUSER_PASSWORD"),
            )
            admin.is_active = True
            admin.is_superuser = True
            admin.save()
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Admin accounts can only be "
                    "initialized if no Accounts exist"
                )
            )

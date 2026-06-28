from __future__ import annotations

import getpass

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Create a superadmin (superuser) account.\n\n"
        "Usage:\n"
        "  python manage.py create_superadmin\n"
        "  python manage.py create_superadmin --username admin --email admin@church.org\n"
        "  python manage.py create_superadmin --username admin --email admin@church.org --password secret\n"
    )

    def add_arguments(self, parser):
        parser.add_argument("--username", default=None, help="Superadmin username (default: admin)")
        parser.add_argument("--email", default=None, help="Superadmin email address")
        parser.add_argument(
            "--password",
            default=None,
            help="Superadmin password. Omit to be prompted securely.",
        )

    def handle(self, *args, **options):
        User = get_user_model()

        username = options["username"] or input("Username [admin]: ").strip() or "admin"
        email = options["email"] or input("Email address: ").strip()

        password = options["password"]
        if not password:
            while True:
                password = getpass.getpass("Password: ")
                confirm = getpass.getpass("Password (again): ")
                if password == confirm:
                    break
                self.stderr.write(self.style.ERROR("Passwords do not match. Try again."))

        if User.objects.filter(username=username).exists():
            self.stderr.write(self.style.ERROR(f"User '{username}' already exists."))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superadmin '{username}' created successfully."))

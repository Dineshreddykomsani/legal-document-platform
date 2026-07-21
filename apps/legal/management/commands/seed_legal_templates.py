from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.legal.seed_data import seed_default_document_templates


class Command(BaseCommand):
    help = "Seed legal document templates."

    def handle(self, *args, **options):
        created_count = seed_default_document_templates()
        self.stdout.write(self.style.SUCCESS(f"Created {created_count} missing legal templates."))

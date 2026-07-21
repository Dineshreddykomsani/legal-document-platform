from django.apps import AppConfig


class LegalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.legal"

    def ready(self) -> None:
        from django.db.models.signals import post_migrate

        from apps.legal.seed_data import seed_default_document_templates

        def populate_templates(sender, **kwargs):
            seed_default_document_templates()

        post_migrate.connect(populate_templates, dispatch_uid="seed_default_templates_on_migrate")

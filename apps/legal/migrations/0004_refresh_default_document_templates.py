from django.db import migrations


def refresh_default_document_templates(apps, schema_editor):
    from apps.legal.seed_data import DEFAULT_TEMPLATES, LEGACY_DEFAULT_TEMPLATES

    DocumentTemplate = apps.get_model("legal", "DocumentTemplate")

    for template in DEFAULT_TEMPLATES:
        document_type = str(template["document_type"])
        legacy = LEGACY_DEFAULT_TEMPLATES.get(document_type)
        existing = DocumentTemplate.objects.filter(document_type=document_type).first()

        if existing is None:
            DocumentTemplate.objects.create(**template, is_active=True)
            continue

        if not legacy:
            continue

        is_untouched_default = (
            existing.name == legacy["name"]
            and existing.description == legacy["description"]
            and existing.required_fields == legacy["required_fields"]
            and existing.body == legacy["body"]
        )
        if is_untouched_default:
            existing.name = template["name"]
            existing.description = template["description"]
            existing.required_fields = template["required_fields"]
            existing.body = template["body"]
            existing.is_active = True
            existing.save(update_fields=["name", "description", "required_fields", "body", "is_active", "updated_at"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("legal", "0003_seed_default_document_templates"),
    ]

    operations = [
        migrations.RunPython(refresh_default_document_templates, noop_reverse),
    ]

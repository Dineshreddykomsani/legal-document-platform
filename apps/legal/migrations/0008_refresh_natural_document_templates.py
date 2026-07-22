from django.db import migrations


def refresh_natural_document_templates(apps, schema_editor):
    from apps.legal.seed_data import seed_default_document_templates

    seed_default_document_templates()


class Migration(migrations.Migration):

    dependencies = [
        ("legal", "0007_refresh_professional_template_content"),
    ]

    operations = [
        migrations.RunPython(refresh_natural_document_templates, migrations.RunPython.noop),
    ]

from django.db import migrations


def refresh_professional_template_content(apps, schema_editor):
    from apps.legal.seed_data import seed_default_document_templates

    seed_default_document_templates()


class Migration(migrations.Migration):

    dependencies = [
        ("legal", "0006_seed_template_gallery"),
    ]

    operations = [
        migrations.RunPython(refresh_professional_template_content, migrations.RunPython.noop),
    ]

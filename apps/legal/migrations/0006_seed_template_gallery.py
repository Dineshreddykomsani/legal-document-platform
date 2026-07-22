from django.db import migrations


def seed_template_gallery(apps, schema_editor):
    from apps.legal.seed_data import seed_default_document_templates

    seed_default_document_templates()


class Migration(migrations.Migration):

    dependencies = [
        ("legal", "0005_template_gallery_branding"),
    ]

    operations = [
        migrations.RunPython(seed_template_gallery, migrations.RunPython.noop),
    ]

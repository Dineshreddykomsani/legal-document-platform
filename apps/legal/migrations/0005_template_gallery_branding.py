from django.db import migrations, models
import django.db.models.deletion


def normalize_existing_template_layouts(apps, schema_editor):
    DocumentTemplate = apps.get_model("legal", "DocumentTemplate")
    for template in DocumentTemplate.objects.filter(layout_id="classic"):
        template.layout_id = "modern_corporate"
        template.theme = "Modern Corporate"
        template.header_style = "band"
        template.footer_style = "rule"
        template.color_scheme = {"primary": "#0f766e", "secondary": "#334155", "accent": "#14b8a6"}
        template.font = "Helvetica"
        template.save(
            update_fields=[
                "layout_id",
                "theme",
                "header_style",
                "footer_style",
                "color_scheme",
                "font",
                "updated_at",
            ]
        )


class Migration(migrations.Migration):

    dependencies = [
        ("legal", "0004_refresh_default_document_templates"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="documenttemplate",
            options={"ordering": ["document_type", "name"]},
        ),
        migrations.AlterField(
            model_name="documenttemplate",
            name="document_type",
            field=models.CharField(
                choices=[
                    ("nda", "NDA"),
                    ("employment_letter", "Employment Letter"),
                    ("service_agreement", "Service Agreement"),
                    ("offer_letter", "Offer Letter"),
                    ("consulting_agreement", "Consulting Agreement"),
                    ("internship_letter", "Internship Letter"),
                    ("experience_letter", "Experience Letter"),
                    ("relieving_letter", "Relieving Letter"),
                    ("vendor_agreement", "Vendor Agreement"),
                    ("partnership_agreement", "Partnership Agreement"),
                    ("freelancer_agreement", "Freelancer Agreement"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="legaldocument",
            name="document_type",
            field=models.CharField(
                choices=[
                    ("nda", "NDA"),
                    ("employment_letter", "Employment Letter"),
                    ("service_agreement", "Service Agreement"),
                    ("offer_letter", "Offer Letter"),
                    ("consulting_agreement", "Consulting Agreement"),
                    ("internship_letter", "Internship Letter"),
                    ("experience_letter", "Experience Letter"),
                    ("relieving_letter", "Relieving Letter"),
                    ("vendor_agreement", "Vendor Agreement"),
                    ("partnership_agreement", "Partnership Agreement"),
                    ("freelancer_agreement", "Freelancer Agreement"),
                ],
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="documenttemplate",
            name="color_scheme",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="documenttemplate",
            name="font",
            field=models.CharField(default="Helvetica", max_length=80),
        ),
        migrations.AddField(
            model_name="documenttemplate",
            name="footer_style",
            field=models.CharField(default="standard", max_length=80),
        ),
        migrations.AddField(
            model_name="documenttemplate",
            name="header_style",
            field=models.CharField(default="letterhead", max_length=80),
        ),
        migrations.AddField(
            model_name="documenttemplate",
            name="layout_id",
            field=models.CharField(default="classic", max_length=80),
        ),
        migrations.AddField(
            model_name="documenttemplate",
            name="preview_image",
            field=models.ImageField(blank=True, null=True, upload_to="template_previews/"),
        ),
        migrations.AddField(
            model_name="documenttemplate",
            name="theme",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="legaldocument",
            name="branding",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="legaldocument",
            name="company_logo",
            field=models.ImageField(blank=True, null=True, upload_to="company_logos/"),
        ),
        migrations.AddField(
            model_name="legaldocument",
            name="template",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="legal.documenttemplate",
            ),
        ),
        migrations.RunPython(normalize_existing_template_layouts, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="documenttemplate",
            constraint=models.UniqueConstraint(fields=("document_type", "layout_id"), name="unique_template_layout_per_type"),
        ),
    ]

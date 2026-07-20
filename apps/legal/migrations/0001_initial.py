from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DocumentTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                (
                    "document_type",
                    models.CharField(
                        choices=[
                            ("nda", "NDA"),
                            ("employment_letter", "Employment Letter"),
                            ("service_agreement", "Service Agreement"),
                            ("offer_letter", "Offer Letter"),
                        ],
                        max_length=32,
                        unique=True,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("required_fields", models.JSONField(default=list)),
                ("body", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="LegalDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                (
                    "document_type",
                    models.CharField(
                        choices=[
                            ("nda", "NDA"),
                            ("employment_letter", "Employment Letter"),
                            ("service_agreement", "Service Agreement"),
                            ("offer_letter", "Offer Letter"),
                        ],
                        max_length=32,
                    ),
                ),
                ("content", models.TextField()),
                ("status", models.CharField(choices=[("draft", "Draft"), ("generated", "Generated")], default="draft", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-updated_at", "-created_at"]},
        ),
        migrations.CreateModel(
            name="DocumentVersion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version_number", models.PositiveIntegerField()),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "legal_document",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="versions", to="legal.legaldocument"),
                ),
            ],
            options={"ordering": ["-version_number"]},
        ),
        migrations.AddIndex(
            model_name="legaldocument",
            index=models.Index(fields=["document_type", "status"], name="legal_legal_documen_4cfd8e_idx"),
        ),
        migrations.AddIndex(
            model_name="legaldocument",
            index=models.Index(fields=["updated_at"], name="legal_legal_updated_fed3e5_idx"),
        ),
        migrations.AddConstraint(
            model_name="documentversion",
            constraint=models.UniqueConstraint(fields=("legal_document", "version_number"), name="unique_document_version_number"),
        ),
    ]

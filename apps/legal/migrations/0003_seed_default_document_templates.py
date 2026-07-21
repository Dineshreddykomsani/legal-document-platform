from django.db import migrations


def seed_default_document_templates(apps, schema_editor):
    DocumentTemplate = apps.get_model("legal", "DocumentTemplate")

    defaults = [
        {
            "name": "Employment Letter",
            "document_type": "employment_letter",
            "description": "Confirms role, compensation, start date, and employment terms.",
            "required_fields": [
                {"name": "employee_name", "label": "Employee Name"},
                {"name": "company_name", "label": "Company Name"},
                {"name": "job_title", "label": "Job Title"},
                {"name": "start_date", "label": "Start Date"},
                {"name": "salary", "label": "Salary"},
            ],
            "body": """EMPLOYMENT LETTER

Dear {{ employee_name }},

{{ company_name }} is pleased to offer you the position of {{ job_title }}, starting {{ start_date }}.

Your compensation will be {{ salary }}, subject to applicable withholdings and company policies.

You agree to comply with company policies, maintain confidentiality, and perform your duties professionally.

This letter summarizes the principal terms of employment and does not alter any applicable at-will employment status unless required by law.""",
            "is_active": True,
        },
        {
            "name": "Offer Letter",
            "document_type": "offer_letter",
            "description": "Sets out offer details for a candidate.",
            "required_fields": [
                {"name": "candidate_name", "label": "Candidate Name"},
                {"name": "company_name", "label": "Company Name"},
                {"name": "role", "label": "Role"},
                {"name": "joining_date", "label": "Joining Date"},
                {"name": "compensation", "label": "Compensation"},
            ],
            "body": """OFFER LETTER

Dear {{ candidate_name }},

We are pleased to offer you the role of {{ role }} at {{ company_name }}, with an expected joining date of {{ joining_date }}.

Your total compensation will be {{ compensation }}, subject to taxes, deductions, and company policies.

This offer is contingent on completion of applicable background checks, execution of onboarding documents, and continued business need.

Please confirm acceptance by signing and returning this letter.""",
            "is_active": True,
        },
        {
            "name": "Mutual Non-Disclosure Agreement",
            "document_type": "nda",
            "description": "Protects confidential information exchanged between two parties.",
            "required_fields": [
                {"name": "party_one", "label": "Disclosing Party"},
                {"name": "party_two", "label": "Receiving Party"},
                {"name": "effective_date", "label": "Effective Date"},
                {"name": "term", "label": "Confidentiality Term"},
                {"name": "governing_law", "label": "Governing Law"},
            ],
            "body": """NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement is entered into by {{ party_one }} and {{ party_two }} as of {{ effective_date }}.

1. Confidential Information. Each party may disclose non-public business, technical, financial, or strategic information to the other party.

2. Obligations. The receiving party will protect confidential information using reasonable care and use it only for evaluating or performing the business relationship.

3. Exclusions. Confidential information does not include information that is public, independently developed, or lawfully received from a third party.

4. Term. These obligations remain in effect for {{ term }}.

5. Governing Law. This Agreement is governed by the laws of {{ governing_law }}.""",
            "is_active": True,
        },
        {
            "name": "Service Agreement",
            "document_type": "service_agreement",
            "description": "Defines services, fees, timeline, IP ownership, and termination.",
            "required_fields": [
                {"name": "client_name", "label": "Client Name"},
                {"name": "provider_name", "label": "Service Provider"},
                {"name": "services", "label": "Services"},
                {"name": "fees", "label": "Fees"},
                {"name": "term", "label": "Term"},
            ],
            "body": """SERVICE AGREEMENT

This Service Agreement is between {{ client_name }} and {{ provider_name }}.

1. Services. {{ provider_name }} will provide the following services: {{ services }}.

2. Fees. {{ client_name }} will pay {{ fees }} according to mutually agreed invoice terms.

3. Term. This Agreement will remain effective for {{ term }} unless terminated earlier under this Agreement.

4. Deliverables and IP. Deliverables are owned by {{ client_name }} after full payment, except for provider background technology.

5. Termination. Either party may terminate for material breach if the breach is not cured within a reasonable written notice period.""",
            "is_active": True,
        },
    ]

    for template in defaults:
        DocumentTemplate.objects.get_or_create(
            document_type=template["document_type"],
            defaults=template,
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("legal", "0002_rename_legal_legal_documen_4cfd8e_idx_legal_legal_documen_f7bf8e_idx_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_default_document_templates, noop_reverse),
    ]

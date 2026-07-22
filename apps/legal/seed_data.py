from __future__ import annotations

from copy import deepcopy
from typing import Any

from django.db import transaction

from apps.legal.models import DocumentTemplate, DocumentType


LEGACY_DEFAULT_TEMPLATES: dict[str, dict[str, Any]] = {
    "employment_letter": {
        "name": "Employment Letter",
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
    },
    "offer_letter": {
        "name": "Offer Letter",
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
    },
    "nda": {
        "name": "Mutual Non-Disclosure Agreement",
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
    },
    "service_agreement": {
        "name": "Service Agreement",
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
    },
}


DEFAULT_TEMPLATES: list[dict[str, Any]] = [
    {
        "name": "Employment Agreement",
        "document_type": DocumentType.EMPLOYMENT_LETTER,
        "description": "Comprehensive employment agreement covering duties, compensation, conduct, confidentiality, IP, and termination.",
        "required_fields": [
            {"name": "employee_name", "label": "Employee Name"},
            {"name": "employee_address", "label": "Employee Address"},
            {"name": "company_name", "label": "Company Name"},
            {"name": "company_address", "label": "Company Address"},
            {"name": "job_title", "label": "Job Title"},
            {"name": "department", "label": "Department"},
            {"name": "reporting_manager", "label": "Reporting Manager"},
            {"name": "start_date", "label": "Start Date"},
            {"name": "work_location", "label": "Work Location"},
            {"name": "salary", "label": "Annual CTC / Salary"},
            {"name": "probation_period", "label": "Probation Period"},
            {"name": "notice_period", "label": "Notice Period"},
            {"name": "governing_law", "label": "Governing Law"},
        ],
        "body": """EMPLOYMENT AGREEMENT

This Employment Agreement (the "Agreement") is made on the date of acceptance between {{ company_name }}, having its principal office at {{ company_address }} (the "Company"), and {{ employee_name }}, residing at {{ employee_address }} (the "Employee").

1. Appointment and Commencement
1.1 The Company appoints the Employee as {{ job_title }} in the {{ department }} department with effect from {{ start_date }}.
1.2 The Employee will report to {{ reporting_manager }} or to any other manager designated by the Company.
1.3 The Employee's normal place of work will be {{ work_location }}, subject to reasonable business travel, remote-work directions, or reassignment consistent with the role.

2. Duties and Standard of Performance
2.1 The Employee shall devote full working time, skill, and attention to the Company's business and shall perform duties assigned by the Company in good faith.
2.2 The Employee shall comply with lawful instructions, internal policies, information-security requirements, and all applicable laws and professional standards.
2.3 The Employee shall not engage in outside employment, consulting, or business activity that conflicts with the Company's interests without prior written approval.

3. Compensation, Benefits, and Deductions
3.1 The Employee's annual cost to company / salary package is {{ salary }}, payable in accordance with the Company's payroll cycle and subject to statutory deductions and withholdings.
3.2 The package may include fixed pay, variable pay, allowances, employer contributions, insurance, retirement benefits, and other benefits described in Schedule 1 or Company policy.
3.3 Variable pay, incentives, bonuses, and reimbursements are discretionary unless expressly stated in writing and are subject to performance, eligibility, policy conditions, and applicable tax law.
3.4 The Employee is responsible for submitting accurate tax, bank, identity, and reimbursement documentation requested by the Company.

4. Probation, Working Hours, and Leave
4.1 The Employee will serve a probation period of {{ probation_period }}. Confirmation of employment is subject to satisfactory performance, conduct, attendance, and completion of onboarding requirements.
4.2 Normal working hours, weekly offs, holidays, attendance recording, overtime eligibility, and flexible-work arrangements will be governed by Company policy and applicable law.
4.3 The Employee will be eligible for leave, holidays, health coverage, and other benefits under the Company's policies as amended from time to time.

5. Confidentiality and Non-Disclosure
5.1 The Employee shall keep confidential all non-public information relating to the Company, its affiliates, clients, vendors, employees, pricing, products, source code, systems, strategy, finances, processes, trade secrets, and personal data.
5.2 Confidential information may be used only for authorized Company work and may not be disclosed except to persons with a legitimate business need and equivalent confidentiality obligations.
5.3 The confidentiality obligations apply during employment and continue after termination for so long as the information remains confidential or protected by law.

6. Intellectual Property
6.1 All inventions, works of authorship, software, designs, documentation, discoveries, processes, improvements, data models, reports, and other materials created, conceived, reduced to practice, or contributed to by the Employee in the course of employment or using Company resources are the exclusive property of the Company.
6.2 The Employee assigns to the Company all rights, title, and interest in such work product and shall execute documents reasonably required to perfect or enforce those rights.
6.3 Pre-existing materials owned by the Employee may be used in Company work only with prior disclosure and written approval.

7. Data Protection, Systems, and Records
7.1 The Employee shall process personal data only on Company instructions, for legitimate business purposes, and in compliance with applicable privacy and data-protection laws.
7.2 Company devices, accounts, credentials, networks, records, and communications systems remain Company property and may be monitored, accessed, preserved, or restricted as permitted by law and policy.
7.3 The Employee shall promptly report suspected security incidents, data loss, unauthorized access, or policy violations.

8. Code of Conduct and Compliance
8.1 The Employee shall comply with policies on anti-bribery, anti-corruption, harassment prevention, workplace safety, equal opportunity, conflicts of interest, insider information, export controls, sanctions, and acceptable use.
8.2 The Employee represents that entering into this Agreement does not breach any prior employment, confidentiality, non-solicitation, non-compete, or intellectual-property obligation.

9. Non-Solicitation and Restrictive Covenants
9.1 During employment and for twelve months after termination, the Employee shall not solicit Company employees, consultants, customers, prospects, suppliers, or strategic partners with whom the Employee had material dealings, except where prohibited by applicable law.
9.2 Any non-compete restriction will apply only to the extent valid under governing law and only to protect legitimate business interests including confidential information, client relationships, and trade secrets.

10. Termination
10.1 Either party may terminate employment by giving {{ notice_period }} written notice or payment in lieu of notice where permitted by Company policy and applicable law.
10.2 The Company may terminate employment immediately for serious misconduct, fraud, dishonesty, material policy breach, unauthorized disclosure, abandonment of employment, unlawful conduct, or other cause recognized by law.
10.3 On termination, the Employee shall return all Company property, delete Company information from personal devices where directed, complete handover, settle advances, and continue to comply with surviving obligations.

11. General Provisions
11.1 Notices must be in writing and delivered by hand, courier, registered post, or email to the addresses last notified by the parties.
11.2 This Agreement is governed by the laws of {{ governing_law }}. Courts and tribunals having competent jurisdiction under that law shall have jurisdiction, subject to any mandatory dispute process.
11.3 This Agreement, together with schedules and Company policies incorporated by reference, is the entire agreement regarding employment terms and supersedes prior discussions on the same subject.
11.4 Amendments must be in writing and approved by an authorized Company representative. Failure to enforce a provision is not a waiver. Invalid provisions will be severed to the minimum extent required. The Employee may not assign this Agreement.

Schedule 1 - Compensation and Benefits
A. Annual CTC / salary package: {{ salary }}.
B. Benefits and allowances: As per Company policy and eligibility rules in effect from time to time.
C. Payroll, taxes, statutory contributions, reimbursements, and deductions: As required by law and Company policy.

Execution

For {{ company_name }}

_________________________
Authorized Signatory

Name:
Designation:
Date:

Accepted and agreed by {{ employee_name }}

_________________________
Employee Signature

Name:
Date:""",
    },
    {
        "name": "Offer Letter",
        "document_type": DocumentType.OFFER_LETTER,
        "description": "Production-ready candidate offer letter with joining conditions, CTC, probation, benefits, and acceptance terms.",
        "required_fields": [
            {"name": "candidate_name", "label": "Candidate Name"},
            {"name": "candidate_address", "label": "Candidate Address"},
            {"name": "company_name", "label": "Company Name"},
            {"name": "company_address", "label": "Company Address"},
            {"name": "role", "label": "Role"},
            {"name": "department", "label": "Department"},
            {"name": "reporting_manager", "label": "Reporting Manager"},
            {"name": "joining_date", "label": "Joining Date"},
            {"name": "work_location", "label": "Work Location"},
            {"name": "compensation", "label": "Annual CTC / Compensation"},
            {"name": "probation_period", "label": "Probation Period"},
            {"name": "notice_period", "label": "Notice Period"},
            {"name": "offer_expiry_date", "label": "Offer Expiry Date"},
        ],
        "body": """OFFER LETTER

Date: __________________

To,
{{ candidate_name }}
{{ candidate_address }}

Subject: Offer of Employment as {{ role }}

Dear {{ candidate_name }},

{{ company_name }}, located at {{ company_address }}, is pleased to offer you employment as {{ role }} in the {{ department }} department. This letter summarizes the principal employment terms and the joining formalities that apply before your first day.

1. Position, Reporting, and Joining
1.1 Your proposed joining date is {{ joining_date }}.
1.2 Your work location will be {{ work_location }}, subject to reasonable business requirements, hybrid-work arrangements, client visits, and Company policy.
1.3 You will report to {{ reporting_manager }} or another manager nominated by the Company.
1.4 Your responsibilities will include the duties ordinarily associated with the role, duties described by your manager, and any related responsibilities reasonably assigned by the Company.

2. Compensation and CTC
2.1 Your annual cost to company / total compensation will be {{ compensation }}, subject to taxes, statutory contributions, payroll deductions, and Company policy.
2.2 The compensation structure may include basic salary, allowances, employer contributions, insurance, variable pay, incentives, reimbursements, and benefits. A detailed structure may be issued separately as Annexure A.
2.3 Any bonus, incentive, stock-based benefit, or variable component is discretionary unless expressly stated otherwise in a separate written plan document.

3. Benefits, Leave, and Working Hours
3.1 You will be eligible for employee benefits, insurance, holidays, paid leave, and reimbursements in accordance with the Company's policies and applicable law.
3.2 Working hours, weekly offs, attendance, overtime eligibility, remote-work permissions, and travel reimbursements will be governed by Company policy.

4. Probation and Confirmation
4.1 You will be on probation for {{ probation_period }} from your joining date. The Company may confirm, extend, or end employment during or at the end of probation based on performance, conduct, attendance, business needs, and completion of onboarding requirements.
4.2 Continued employment is conditional on successful background verification, identity and education checks, reference checks, right-to-work verification, and submission of required documents.

5. Company Policies and Confidential Information
5.1 From your joining date, you will be expected to follow the Company's policies on conduct, information security, confidentiality, workplace behavior, conflicts of interest, and use of Company systems.
5.2 Any confidential information shared during onboarding or employment must be used only for Company work and must not be disclosed without authorization.

6. Notice Period
6.1 After joining, either you or the Company may end employment by giving {{ notice_period }} notice, or payment in lieu of notice where permitted by Company policy.
6.2 The Company may withdraw this offer if the conditions in this letter are not completed, information provided by you is inaccurate, or you do not join on the agreed date.

7. Joining Instructions and Acceptance
7.1 Please confirm your acceptance by signing and returning this letter on or before {{ offer_expiry_date }}.
7.2 On your joining date, please carry identity proof, address proof, education and experience records, tax documents, bank details, passport-size photographs where required, and any onboarding forms requested by the Company.
7.3 Detailed employment terms, including confidentiality, intellectual-property ownership, data protection, and post-employment obligations, may be set out in the Company's employment agreement and policies issued at or after joining.

For {{ company_name }}

_________________________
Authorized Signatory

Name:
Designation:
Date:

Accepted by
I, {{ candidate_name }}, accept this offer and confirm that I intend to join {{ company_name }} on {{ joining_date }}.

_________________________
Candidate Signature

Name:
Date:""",
    },
    {
        "name": "Mutual Non-Disclosure Agreement",
        "document_type": DocumentType.NDA,
        "description": "Detailed mutual NDA for business evaluations, transactions, technical discussions, and vendor/client diligence.",
        "required_fields": [
            {"name": "party_one", "label": "Party One"},
            {"name": "party_one_address", "label": "Party One Address"},
            {"name": "party_two", "label": "Party Two"},
            {"name": "party_two_address", "label": "Party Two Address"},
            {"name": "effective_date", "label": "Effective Date"},
            {"name": "purpose", "label": "Purpose"},
            {"name": "term", "label": "Confidentiality Term"},
            {"name": "notice_email", "label": "Notice Email"},
            {"name": "governing_law", "label": "Governing Law"},
        ],
        "body": """MUTUAL NON-DISCLOSURE AGREEMENT

This Mutual Non-Disclosure Agreement (the "Agreement") is entered into as of {{ effective_date }} by and between {{ party_one }}, having an address at {{ party_one_address }}, and {{ party_two }}, having an address at {{ party_two_address }}. Each is a "Party" and together they are the "Parties."

1. Purpose
The Parties wish to exchange information solely to evaluate, discuss, negotiate, or perform the following business purpose: {{ purpose }} (the "Purpose").

2. Definition of Confidential Information
2.1 "Confidential Information" means all non-public information disclosed by or on behalf of a Party, whether oral, written, electronic, visual, or in any other form, including business plans, technical information, software, source code, object code, data, financial information, pricing, customers, vendors, product plans, security information, processes, trade secrets, personal data, analyses, notes, and materials derived from such information.
2.2 Confidential Information includes information disclosed before the effective date if it relates to the Purpose and was treated as confidential when disclosed.

3. Obligations of Receiving Party
3.1 The receiving Party shall use Confidential Information only for the Purpose.
3.2 The receiving Party shall protect Confidential Information using at least reasonable care and no less care than it uses to protect its own similar confidential information.
3.3 The receiving Party may disclose Confidential Information only to its employees, officers, directors, affiliates, professional advisers, contractors, and financing sources who need to know it for the Purpose and are bound by confidentiality obligations at least as protective as this Agreement.
3.4 The receiving Party remains responsible for any breach by persons to whom it discloses Confidential Information.

4. Exclusions
Confidential Information does not include information the receiving Party can demonstrate: (a) is or becomes public without breach of this Agreement; (b) was lawfully known before disclosure; (c) is received from a third party without confidentiality restriction; or (d) is independently developed without use of or reference to Confidential Information.

5. Compelled Disclosure
If a receiving Party is required by law, court order, regulator, or stock exchange rule to disclose Confidential Information, it shall, to the extent legally permitted, give prompt written notice, cooperate in seeking confidential treatment, and disclose only the portion legally required.

6. Ownership and No License
All Confidential Information remains the property of the disclosing Party. No license or transfer of intellectual-property rights is granted except the limited right to use Confidential Information for the Purpose.

7. Data Protection and Security
Each Party shall comply with applicable privacy and data-protection laws when handling personal data. The receiving Party shall maintain administrative, technical, and physical safeguards appropriate to the sensitivity of the Confidential Information and shall promptly notify the disclosing Party of unauthorized access, loss, or disclosure.

8. Return or Destruction
Upon written request or termination of discussions, the receiving Party shall promptly return or destroy Confidential Information, except that one archival copy may be retained for legal, compliance, or backup purposes subject to continuing confidentiality obligations.

9. Term and Survival
This Agreement begins on {{ effective_date }} and continues for {{ term }}. Confidentiality obligations survive for the stated term, and trade-secret obligations continue for as long as the information remains a trade secret under applicable law.

10. No Warranty; No Obligation
Confidential Information is provided "as is." Neither Party makes warranties about accuracy or completeness. Neither Party is obligated to proceed with any transaction, purchase, investment, employment, partnership, or commercial relationship.

11. Remedies
Unauthorized disclosure or misuse may cause irreparable harm for which monetary damages may be inadequate. The disclosing Party may seek injunctive relief, specific performance, and any other remedies available by law without waiving other rights.

12. General Provisions
12.1 Notices must be sent in writing to the relevant Party's address above with a copy by email to {{ notice_email }}.
12.2 This Agreement is governed by the laws of {{ governing_law }}. Courts of competent jurisdiction under that law shall have jurisdiction, subject to any mandatory legal process.
12.3 Neither Party may assign this Agreement without prior written consent, except to a successor in connection with merger, reorganization, or sale of substantially all assets.
12.4 Amendments must be in writing and signed by both Parties. Failure to enforce a right is not a waiver. Invalid provisions will be severed to the minimum extent required. This Agreement is the entire agreement regarding Confidential Information for the Purpose.
12.5 Force majeure excuses delayed performance other than confidentiality, payment, and security obligations to the extent caused by events beyond reasonable control.

Execution

For {{ party_one }}

_________________________
Authorized Signatory

Name:
Designation:
Date:

For {{ party_two }}

_________________________
Authorized Signatory

Name:
Designation:
Date:""",
    },
    {
        "name": "Service Agreement",
        "document_type": DocumentType.SERVICE_AGREEMENT,
        "description": "Full business services agreement with scope, deliverables, acceptance, payment, IP, warranties, liability, and termination.",
        "required_fields": [
            {"name": "client_name", "label": "Client Name"},
            {"name": "client_address", "label": "Client Address"},
            {"name": "provider_name", "label": "Service Provider"},
            {"name": "provider_address", "label": "Provider Address"},
            {"name": "effective_date", "label": "Effective Date"},
            {"name": "services", "label": "Services"},
            {"name": "deliverables", "label": "Deliverables"},
            {"name": "fees", "label": "Fees"},
            {"name": "payment_terms", "label": "Payment Terms"},
            {"name": "term", "label": "Term"},
            {"name": "notice_period", "label": "Notice Period"},
            {"name": "governing_law", "label": "Governing Law"},
        ],
        "body": """SERVICE AGREEMENT

This Service Agreement (the "Agreement") is entered into as of {{ effective_date }} by and between {{ client_name }}, having its principal address at {{ client_address }} (the "Client"), and {{ provider_name }}, having its principal address at {{ provider_address }} (the "Service Provider").

1. Engagement and Scope
1.1 The Client engages the Service Provider to provide the following services: {{ services }}.
1.2 The Service Provider shall perform the services professionally, diligently, and in accordance with the specifications, timelines, and standards set out in this Agreement and any written statement of work.
1.3 Services outside the agreed scope require a written change order describing revised fees, schedule, responsibilities, and deliverables.

2. Deliverables, Milestones, and Acceptance
2.1 The Service Provider shall provide the following deliverables: {{ deliverables }}.
2.2 The Client shall review each deliverable within ten business days after receipt unless a different review period is stated in a statement of work.
2.3 A deliverable is deemed accepted when the Client confirms acceptance in writing, uses it in production or commercial operations, or fails to provide a specific written rejection within the review period.
2.4 Rejected deliverables must be accompanied by reasonable detail. The Service Provider shall correct valid non-conformities within a commercially reasonable period.

3. Client Responsibilities
3.1 The Client shall provide timely access to personnel, systems, information, approvals, and decisions reasonably required for performance.
3.2 The Service Provider is not responsible for delay or failure caused by inaccurate Client materials, late approvals, unavailable systems, or changes in Client requirements.

4. Fees, Taxes, and Payment
4.1 The Client shall pay the Service Provider {{ fees }} in accordance with the following payment terms: {{ payment_terms }}.
4.2 Fees are exclusive of applicable taxes unless expressly stated otherwise. The Client is responsible for taxes other than taxes based on the Service Provider's net income.
4.3 Undisputed overdue amounts may accrue interest at the maximum lawful rate or one percent per month, whichever is lower. The Service Provider may suspend services for material non-payment after written notice and a reasonable cure period.

5. Term and Renewal
5.1 This Agreement begins on {{ effective_date }} and continues for {{ term }} unless terminated earlier.
5.2 Renewal, extension, or additional work requires written agreement or an executed statement of work.

6. Warranties and Compliance
6.1 Each Party represents that it has authority to enter into and perform this Agreement.
6.2 The Service Provider warrants that services will be performed in a professional and workmanlike manner by qualified personnel and will materially conform to agreed specifications.
6.3 The Service Provider shall comply with applicable laws, anti-bribery requirements, sanctions rules, data-protection laws, workplace safety requirements, and Client policies communicated in writing.
6.4 Except as expressly stated, all implied warranties are excluded to the maximum extent permitted by law.

7. Confidentiality and Data Protection
7.1 Each Party shall protect the other Party's non-public business, technical, financial, security, and personal information using reasonable care and shall use it only to perform this Agreement.
7.2 The Service Provider shall process personal data only as necessary to provide the services, follow lawful Client instructions, maintain appropriate safeguards, and promptly notify the Client of unauthorized access or disclosure.
7.3 Confidentiality obligations survive termination for five years, and trade-secret obligations continue for as long as the information remains protected by law.

8. Intellectual Property
8.1 Upon full payment, the Client owns the final deliverables created specifically for the Client under this Agreement, excluding Service Provider background technology.
8.2 The Service Provider retains ownership of pre-existing materials, reusable tools, methodologies, know-how, templates, libraries, generic code, and improvements not uniquely based on Client confidential information.
8.3 To the extent background technology is embedded in a deliverable, the Service Provider grants the Client a perpetual, non-exclusive, worldwide license to use it solely as part of the deliverable.

9. Indemnification
9.1 The Service Provider shall indemnify the Client against third-party claims alleging that a paid deliverable infringes intellectual-property rights, except to the extent caused by Client materials, modifications not made by the Service Provider, or use outside the agreed scope.
9.2 The Client shall indemnify the Service Provider against third-party claims arising from Client materials, Client instructions, unlawful Client use, or breach of this Agreement.
9.3 The indemnified Party must promptly notify the indemnifying Party, allow reasonable control of defense and settlement, and provide cooperation.

10. Limitation of Liability
10.1 Neither Party is liable for indirect, incidental, special, consequential, punitive, or lost-profit damages.
10.2 Each Party's aggregate liability is limited to fees paid or payable under this Agreement during the twelve months preceding the event giving rise to liability.
10.3 The limits do not apply to payment obligations, confidentiality breaches, data misuse, fraud, wilful misconduct, infringement indemnity, or liabilities that cannot be limited by law.

11. Termination
11.1 Either Party may terminate this Agreement for convenience by giving {{ notice_period }} written notice, unless a statement of work provides otherwise.
11.2 Either Party may terminate for material breach if the breach is not cured within thirty days after written notice.
11.3 Upon termination, the Client shall pay for services performed, accepted deliverables, approved expenses, and non-cancellable commitments incurred before termination.
11.4 The Service Provider shall provide reasonable transition assistance at mutually agreed rates and return or destroy Client confidential information upon request.

12. Force Majeure
Neither Party is liable for delay or failure caused by events beyond reasonable control, including natural disasters, war, terrorism, labor disruption, government action, epidemic, utility failure, or widespread network outage, provided the affected Party gives prompt notice and mitigates the impact.

13. Dispute Resolution, Governing Law, and Notices
13.1 Senior representatives shall first attempt in good faith to resolve disputes. If unresolved within thirty days, either Party may pursue remedies before courts of competent jurisdiction.
13.2 This Agreement is governed by the laws of {{ governing_law }}. Courts having competent jurisdiction under that law shall have jurisdiction.
13.3 Notices must be in writing and delivered by hand, courier, registered post, or email to the addresses stated above or any updated address notified in writing.

14. General
14.1 This Agreement is the entire agreement regarding the services and supersedes prior proposals and discussions.
14.2 Amendments and waivers must be in writing and signed by authorized representatives. Failure to enforce a provision is not a waiver.
14.3 Neither Party may assign this Agreement without prior written consent, except to an affiliate or successor in connection with merger, restructuring, or sale of substantially all assets.
14.4 If a provision is invalid, the remaining provisions remain effective and the invalid provision will be replaced by a valid provision closest to the original commercial intent.
14.5 Independent contractor status applies. Nothing creates employment, partnership, agency, franchise, or joint venture.

Schedule 1 - Commercial Summary
A. Services: {{ services }}.
B. Deliverables: {{ deliverables }}.
C. Fees: {{ fees }}.
D. Payment terms: {{ payment_terms }}.
E. Term: {{ term }}.

Execution

For {{ client_name }}

_________________________
Authorized Signatory

Name:
Designation:
Date:

For {{ provider_name }}

_________________________
Authorized Signatory

Name:
Designation:
Date:""",
    },
]


def _matches_legacy_default(template: DocumentTemplate, legacy: dict[str, Any]) -> bool:
    return (
        template.name == legacy["name"]
        and template.description == legacy["description"]
        and template.required_fields == legacy["required_fields"]
        and template.body == legacy["body"]
    )


LAYOUT_VARIANTS: list[dict[str, Any]] = [
    {
        "name": "Modern Corporate",
        "layout_id": "modern_corporate",
        "description": "Clean enterprise letterhead with strong section hierarchy and balanced white space.",
        "theme": "Modern Corporate",
        "header_style": "band",
        "footer_style": "rule",
        "font": "Helvetica",
        "color_scheme": {"primary": "#0f766e", "secondary": "#334155", "accent": "#14b8a6"},
    },
    {
        "name": "Professional Classic",
        "layout_id": "professional_classic",
        "description": "Traditional legal document styling with restrained typography and formal spacing.",
        "theme": "Professional Classic",
        "header_style": "classic",
        "footer_style": "centered",
        "font": "Times-Roman",
        "color_scheme": {"primary": "#1f2937", "secondary": "#475569", "accent": "#64748b"},
    },
    {
        "name": "Executive",
        "layout_id": "executive",
        "description": "Premium executive format with compact header, signature-ready sections, and polished dividers.",
        "theme": "Executive",
        "header_style": "executive",
        "footer_style": "split",
        "font": "Helvetica",
        "color_scheme": {"primary": "#111827", "secondary": "#374151", "accent": "#b45309"},
    },
    {
        "name": "Premium",
        "layout_id": "premium",
        "description": "High-end business document treatment with refined accents and clear commercial schedules.",
        "theme": "Premium",
        "header_style": "premium",
        "footer_style": "rule",
        "font": "Helvetica",
        "color_scheme": {"primary": "#312e81", "secondary": "#475569", "accent": "#7c3aed"},
    },
    {
        "name": "Minimal",
        "layout_id": "minimal",
        "description": "Minimal legal layout for fast review, strong readability, and efficient multi-page output.",
        "theme": "Minimal",
        "header_style": "minimal",
        "footer_style": "minimal",
        "font": "Helvetica",
        "color_scheme": {"primary": "#0f172a", "secondary": "#64748b", "accent": "#0891b2"},
    },
]


ADDITIONAL_DOCUMENTS: list[dict[str, Any]] = [
    {
        "name": "Consulting Agreement",
        "document_type": DocumentType.CONSULTING_AGREEMENT,
        "description": "Independent consultant agreement covering scope, deliverables, fees, IP, compliance, and liability.",
        "required_fields": [
            {"name": "client_name", "label": "Client Name"},
            {"name": "client_address", "label": "Client Address"},
            {"name": "consultant_name", "label": "Consultant Name"},
            {"name": "consultant_address", "label": "Consultant Address"},
            {"name": "effective_date", "label": "Effective Date"},
            {"name": "scope", "label": "Scope of Consulting Services"},
            {"name": "fees", "label": "Fees"},
            {"name": "payment_terms", "label": "Payment Terms"},
            {"name": "term", "label": "Term"},
            {"name": "notice_period", "label": "Notice Period"},
            {"name": "governing_law", "label": "Governing Law"},
        ],
        "body": """CONSULTING AGREEMENT

This Consulting Agreement is entered into as of {{ effective_date }} between {{ client_name }}, located at {{ client_address }}, and {{ consultant_name }}, located at {{ consultant_address }}.

1. Engagement and Scope
1.1 The Client engages the Consultant to provide the following consulting services: {{ scope }}.
1.2 The Consultant shall determine the manner and means of performance while coordinating reasonably with the Client's business requirements.
1.3 The Consultant is an independent contractor and has no authority to bind the Client unless expressly authorized in writing.

2. Deliverables, Review, and Change Control
2.1 Deliverables, milestones, review cycles, and acceptance criteria will be those stated in the applicable statement of work or written project plan.
2.2 Work outside scope requires written approval describing revised fees, timeline, dependencies, and responsibilities.

3. Fees, Expenses, and Taxes
3.1 The Client shall pay {{ fees }} under these payment terms: {{ payment_terms }}.
3.2 Pre-approved expenses will be reimbursed against valid receipts. The Consultant is responsible for all taxes arising from fees paid under this Agreement.

4. Confidentiality, Data Protection, and Security
4.1 The Consultant shall protect Client confidential information, trade secrets, personal data, security information, business plans, customer information, and technical materials.
4.2 Confidential information may be used only for the engagement. The Consultant shall follow reasonable security instructions and promptly report unauthorized access or disclosure.

5. Intellectual Property
5.1 Upon full payment, the Client owns work product specifically created for the Client, excluding Consultant pre-existing tools, know-how, templates, and generalized methods.
5.2 The Consultant grants the Client a perpetual license to embedded background materials necessary to use the work product.

6. Representations, Compliance, and Conflicts
6.1 Each party has authority to enter this Agreement. The Consultant shall comply with applicable laws, anti-bribery rules, sanctions requirements, privacy obligations, and Client policies communicated in writing.
6.2 The Consultant shall disclose conflicts of interest and shall not use third-party confidential information without authorization.

7. Non-Solicitation
During the engagement and for twelve months thereafter, neither party shall knowingly solicit for employment the other party's personnel materially involved in the engagement, except through general solicitations not targeted at such personnel.

8. Indemnity and Limitation of Liability
8.1 Each party shall indemnify the other for third-party claims arising from its breach, negligence, wilful misconduct, or infringement by materials it supplies.
8.2 Neither party is liable for indirect or consequential damages. Aggregate liability is limited to fees paid or payable in the six months before the claim, except for confidentiality breaches, IP infringement, fraud, wilful misconduct, or unpaid fees.

9. Term and Termination
9.1 This Agreement continues for {{ term }} unless terminated earlier.
9.2 Either party may terminate by giving {{ notice_period }} written notice or immediately for uncured material breach after thirty days' notice.
9.3 On termination, the Client shall pay for completed work, approved expenses, and non-cancellable commitments.

10. General
This Agreement is governed by {{ governing_law }}. Disputes will first be escalated to senior representatives, then submitted to competent courts unless the parties agree to arbitration. Notices must be written. Force majeure excuses delayed performance except payment and confidentiality obligations. Amendments must be written. Invalid provisions are severed. No waiver is implied. This Agreement is the entire agreement and may not be assigned without consent except to a successor.

Execution

For {{ client_name }}

_________________________
Authorized Signatory

Name:
Designation:
Date:

Accepted by {{ consultant_name }}

_________________________
Consultant Signature

Name:
Date:""",
    },
    {
        "name": "Internship Letter",
        "document_type": DocumentType.INTERNSHIP_LETTER,
        "description": "Structured internship appointment letter with learning scope, stipend, conduct, confidentiality, and completion terms.",
        "required_fields": [
            {"name": "intern_name", "label": "Intern Name"},
            {"name": "company_name", "label": "Company Name"},
            {"name": "department", "label": "Department"},
            {"name": "mentor_name", "label": "Mentor Name"},
            {"name": "start_date", "label": "Start Date"},
            {"name": "end_date", "label": "End Date"},
            {"name": "work_location", "label": "Work Location"},
            {"name": "stipend", "label": "Stipend"},
            {"name": "working_hours", "label": "Working Hours"},
        ],
        "body": """INTERNSHIP APPOINTMENT LETTER

Dear {{ intern_name }},

{{ company_name }} offers you an internship in the {{ department }} department from {{ start_date }} to {{ end_date }} at {{ work_location }}.

1. Purpose and Learning Scope
1.1 The internship is intended to provide supervised practical exposure, project participation, and professional learning.
1.2 You will work under {{ mentor_name }} and perform tasks assigned for training, research, documentation, analysis, product support, or operational assistance.

2. Stipend, Hours, and Leave
2.1 You will receive a stipend of {{ stipend }}, subject to applicable deductions.
2.2 Your expected working hours are {{ working_hours }}. Leave, holidays, remote work, and attendance requirements will follow Company policy and mentor approval.

3. Conduct and Compliance
You must follow Company policies on workplace behavior, harassment prevention, safety, information security, acceptable use, anti-bribery, conflicts of interest, and professional communication.

4. Confidentiality, Data Protection, and IP
4.1 You must keep confidential all Company and client information received during the internship.
4.2 Work product created during assigned internship activities belongs to the Company, subject to mandatory academic rights required by law or approved in writing.
4.3 Personal data must be handled only as instructed and security incidents must be reported immediately.

5. No Employment Guarantee
This internship does not create a promise of employment, employee benefits, or continued engagement after {{ end_date }}.

6. Termination and Completion
Either party may end the internship with reasonable written notice. The Company may end it immediately for misconduct, policy breach, poor attendance, unauthorized disclosure, or business reasons. Completion letters are subject to satisfactory conduct, handover, return of property, and completion of assigned work.

7. Internship Records
Subject to satisfactory attendance, conduct, handover, and completion of assigned work, the Company may issue an internship completion certificate or experience confirmation in its standard format.

8. Acknowledgment
This letter, together with applicable Company policies and onboarding instructions, records the internship arrangement. Any change to the internship period, stipend, location, or department should be confirmed in writing.

For {{ company_name }}

_________________________
Authorized Signatory

Name:
Designation:
Date:

Accepted by {{ intern_name }}

_________________________
Intern Signature

Name:
Date:""",
    },
    {
        "name": "Experience Letter",
        "document_type": DocumentType.EXPERIENCE_LETTER,
        "description": "Formal employment experience certificate confirming tenure, role, department, and conduct.",
        "required_fields": [
            {"name": "employee_name", "label": "Employee Name"},
            {"name": "company_name", "label": "Company Name"},
            {"name": "job_title", "label": "Job Title"},
            {"name": "department", "label": "Department"},
            {"name": "start_date", "label": "Start Date"},
            {"name": "end_date", "label": "End Date"},
            {"name": "conduct_summary", "label": "Conduct / Performance Summary"},
            {"name": "issuer_name", "label": "Issuer Name"},
            {"name": "issuer_title", "label": "Issuer Title"},
        ],
        "body": """EXPERIENCE LETTER

To Whom It May Concern,

This is to certify that {{ employee_name }} was employed with {{ company_name }} as {{ job_title }} in the {{ department }} department from {{ start_date }} to {{ end_date }}.

During this period, {{ employee_name }} carried out responsibilities associated with the role, worked with internal teams, and completed assigned duties in accordance with Company expectations.

As per Company records, the employee's conduct and performance summary is as follows: {{ conduct_summary }}.

This letter is issued on the basis of records available with the Company for employment verification and professional reference purposes. It does not release the employee from any continuing confidentiality, return-of-property, or post-employment obligations that may apply.

For {{ company_name }}

_________________________
Authorized Signatory

{{ issuer_name }}
{{ issuer_title }}
Date:""",
    },
    {
        "name": "Relieving Letter",
        "document_type": DocumentType.RELIEVING_LETTER,
        "description": "Formal relieving confirmation covering resignation acceptance, last working day, handover, and dues.",
        "required_fields": [
            {"name": "employee_name", "label": "Employee Name"},
            {"name": "company_name", "label": "Company Name"},
            {"name": "job_title", "label": "Job Title"},
            {"name": "resignation_date", "label": "Resignation Date"},
            {"name": "last_working_day", "label": "Last Working Day"},
            {"name": "handover_status", "label": "Handover Status"},
            {"name": "issuer_name", "label": "Issuer Name"},
            {"name": "issuer_title", "label": "Issuer Title"},
        ],
        "body": """RELIEVING LETTER

Dear {{ employee_name }},

This confirms that {{ company_name }} accepted your resignation dated {{ resignation_date }} from the position of {{ job_title }}. Your last working day with the Company was {{ last_working_day }}.

You are relieved from your duties effective close of business on {{ last_working_day }}, subject to completion of exit formalities and continuing obligations.

Our records reflect the following handover status: {{ handover_status }}. Any remaining Company property, credentials, documents, data, or advances must be returned or settled if later identified.

Full and final settlement, statutory records, tax documents, and applicable payments will be processed according to Company policy and applicable law. Confidentiality, data protection, intellectual-property ownership, and other post-employment obligations continue after your relieving date.

We thank you for your service and wish you success in your future endeavors.

For {{ company_name }}

_________________________
Authorized Signatory

{{ issuer_name }}
{{ issuer_title }}
Date:""",
    },
    {
        "name": "Vendor Agreement",
        "document_type": DocumentType.VENDOR_AGREEMENT,
        "description": "Commercial vendor agreement for goods or services with delivery, quality, compliance, and indemnity terms.",
        "required_fields": [
            {"name": "customer_name", "label": "Customer Name"},
            {"name": "customer_address", "label": "Customer Address"},
            {"name": "vendor_name", "label": "Vendor Name"},
            {"name": "vendor_address", "label": "Vendor Address"},
            {"name": "effective_date", "label": "Effective Date"},
            {"name": "goods_or_services", "label": "Goods or Services"},
            {"name": "fees", "label": "Fees"},
            {"name": "payment_terms", "label": "Payment Terms"},
            {"name": "term", "label": "Term"},
            {"name": "governing_law", "label": "Governing Law"},
        ],
        "body": """VENDOR AGREEMENT

This Vendor Agreement is made as of {{ effective_date }} between {{ customer_name }}, at {{ customer_address }}, and {{ vendor_name }}, at {{ vendor_address }}.

1. Supply and Scope
The Vendor shall provide the following goods or services: {{ goods_or_services }}. Specifications, quantities, service levels, delivery locations, and timelines may be stated in purchase orders or statements of work.

2. Orders, Delivery, and Acceptance
Orders are binding only when issued or accepted in writing. The Customer may inspect deliverables and reject non-conforming items. Risk of loss transfers only on accepted delivery unless otherwise agreed.

3. Fees and Payment
Fees are {{ fees }} and payment terms are {{ payment_terms }}. Invoices must include purchase order references, tax information, and reasonable supporting documentation.

4. Quality, Compliance, and Records
The Vendor warrants that goods and services will conform to specifications, be free from material defects, comply with applicable laws, and not infringe third-party rights. The Vendor shall maintain records sufficient to demonstrate compliance.

5. Confidentiality, Data, and Security
Each party shall protect confidential information. The Vendor shall process Customer data only to perform the agreement, maintain appropriate safeguards, and notify the Customer of security incidents.

6. IP, Indemnity, and Insurance
Customer materials remain Customer property. Vendor background materials remain Vendor property. The Vendor shall indemnify the Customer for claims arising from defective goods, infringement, data breach, unlawful conduct, or Vendor negligence. The Vendor shall maintain commercially reasonable insurance.

7. Liability, Term, and Termination
This Agreement continues for {{ term }}. Either party may terminate for uncured material breach. Liability exclusions do not apply to unpaid fees, confidentiality breaches, data misuse, infringement, fraud, wilful misconduct, or indemnity obligations.

8. General
Force majeure excuses delayed performance except payment and confidentiality obligations. Notices must be written. This Agreement is governed by {{ governing_law }}. Amendments, waivers, assignment, severability, and entire agreement principles apply in customary commercial form.

Execution

For {{ customer_name }}

_________________________
Authorized Signatory

Name:
Designation:
Date:

Accepted by {{ vendor_name }}

_________________________
Authorized Signatory

Name:
Designation:
Date:""",
    },
    {
        "name": "Partnership Agreement",
        "document_type": DocumentType.PARTNERSHIP_AGREEMENT,
        "description": "Business partnership agreement with contributions, governance, profit sharing, duties, exits, and disputes.",
        "required_fields": [
            {"name": "partner_one", "label": "Partner One"},
            {"name": "partner_two", "label": "Partner Two"},
            {"name": "business_name", "label": "Business Name"},
            {"name": "business_purpose", "label": "Business Purpose"},
            {"name": "effective_date", "label": "Effective Date"},
            {"name": "capital_contributions", "label": "Capital Contributions"},
            {"name": "profit_share", "label": "Profit / Loss Share"},
            {"name": "management_roles", "label": "Management Roles"},
            {"name": "term", "label": "Term"},
            {"name": "governing_law", "label": "Governing Law"},
        ],
        "body": """PARTNERSHIP AGREEMENT

This Partnership Agreement is entered into as of {{ effective_date }} by {{ partner_one }} and {{ partner_two }} for the business operated as {{ business_name }}.

1. Formation and Purpose
The partners associate to conduct the following business purpose: {{ business_purpose }}. The partnership shall operate under applicable law and any registrations, licenses, or tax requirements.

2. Contributions and Ownership
Capital and non-cash contributions are: {{ capital_contributions }}. Additional contributions require written consent. Partnership property is owned by the partnership and not by individual partners.

3. Profits, Losses, and Accounts
Profits and losses will be shared as follows: {{ profit_share }}. Accurate books, bank accounts, tax filings, and financial records shall be maintained and made available to all partners.

4. Management and Duties
Management roles are: {{ management_roles }}. Partners owe duties of good faith, loyalty, care, confidentiality, conflict disclosure, and compliance with law.

5. Restrictions
No partner may bind the partnership outside ordinary business, admit a new partner, borrow material amounts, sell major assets, assign partnership interest, or enter affiliated transactions without required approval.

6. Confidentiality, IP, and Data
Business information, customer data, trade secrets, and partnership records must be protected. IP created for the partnership belongs to the partnership unless otherwise agreed in writing.

7. Term, Withdrawal, and Termination
The partnership continues for {{ term }}. Withdrawal, expulsion, death, incapacity, deadlock, or material breach triggers valuation, buyout, wind-down, or dissolution procedures as agreed by the partners or required by law.

8. Indemnity, Liability, and Disputes
Partners shall indemnify the partnership for losses caused by fraud, wilful misconduct, unauthorized acts, or material breach. Disputes must first be discussed in good faith, then submitted to mediation or competent courts under {{ governing_law }}.

9. General
Notices must be written. Amendments require written partner approval. Waiver is not implied. Invalid provisions are severed. This Agreement is the entire partnership agreement.

Execution

{{ partner_one }}

_________________________
Partner Signature

Name:
Date:

{{ partner_two }}

_________________________
Partner Signature

Name:
Date:""",
    },
    {
        "name": "Freelancer Agreement",
        "document_type": DocumentType.FREELANCER_AGREEMENT,
        "description": "Freelancer engagement agreement for project work with milestones, payment, IP, confidentiality, and termination.",
        "required_fields": [
            {"name": "client_name", "label": "Client Name"},
            {"name": "freelancer_name", "label": "Freelancer Name"},
            {"name": "effective_date", "label": "Effective Date"},
            {"name": "project_scope", "label": "Project Scope"},
            {"name": "deliverables", "label": "Deliverables"},
            {"name": "fees", "label": "Fees"},
            {"name": "payment_terms", "label": "Payment Terms"},
            {"name": "deadline", "label": "Deadline"},
            {"name": "governing_law", "label": "Governing Law"},
        ],
        "body": """FREELANCER AGREEMENT

This Freelancer Agreement is entered into as of {{ effective_date }} between {{ client_name }} and {{ freelancer_name }}.

1. Project Scope
The Freelancer shall perform the following project work: {{ project_scope }}. Deliverables are: {{ deliverables }}. The expected completion deadline is {{ deadline }}.

2. Milestones and Acceptance
The Client shall review deliverables within a reasonable period and provide specific feedback. Use of a deliverable in production or failure to reject with reasons constitutes acceptance.

3. Fees and Payment
Fees are {{ fees }} payable according to {{ payment_terms }}. Late changes, new requirements, or additional rounds beyond scope require written approval and may increase fees.

4. Independent Contractor
The Freelancer is an independent contractor responsible for tools, taxes, insurance, and work methods. No employment, agency, partnership, or benefits relationship is created.

5. Confidentiality, Data Protection, and Conduct
The Freelancer shall protect Client confidential information, personal data, credentials, brand materials, and business records, use them only for the project, and return or delete them on request.

6. Intellectual Property
Upon full payment, Client owns final deliverables created specifically for the project. Freelancer retains pre-existing materials, portfolio know-how, tools, concepts not selected by Client, and generic methods, while granting Client the license needed to use embedded background materials.

7. Warranties, Indemnity, and Liability
The Freelancer warrants original work or properly licensed materials and professional performance. Each party indemnifies the other for breach, infringement caused by its materials, negligence, fraud, or unlawful conduct. Liability excludes indirect damages and is capped at fees paid, except for confidentiality, IP, fraud, wilful misconduct, or unpaid fees.

8. Termination and General
Either party may terminate for uncured material breach or by reasonable written notice. Client shall pay for accepted work and authorized work in progress. Force majeure, notices, amendments, waiver, severability, entire agreement, assignment, governing law, and jurisdiction are governed by customary commercial principles under {{ governing_law }}.

Execution

For {{ client_name }}

_________________________
Authorized Signatory

Name:
Designation:
Date:

Accepted by {{ freelancer_name }}

_________________________
Freelancer Signature

Name:
Date:""",
    },
]


def _gallery_source_templates() -> list[dict[str, Any]]:
    return [*DEFAULT_TEMPLATES, *ADDITIONAL_DOCUMENTS]


def _gallery_templates() -> list[dict[str, Any]]:
    templates: list[dict[str, Any]] = []
    for source in _gallery_source_templates():
        for variant in LAYOUT_VARIANTS:
            name = source["name"] if variant["layout_id"] == "modern_corporate" else f"{source['name']} - {variant['name']}"
            templates.append(
                {
                    **deepcopy(source),
                    "name": name,
                    "description": f"{source['description']} {variant['description']}",
                    "layout_id": variant["layout_id"],
                    "theme": variant["theme"],
                    "header_style": variant["header_style"],
                    "footer_style": variant["footer_style"],
                    "font": variant["font"],
                    "color_scheme": variant["color_scheme"],
                    "is_active": True,
                }
            )
    return templates


@transaction.atomic
def seed_default_document_templates() -> int:
    created_count = 0
    has_gallery_fields = any(field.name == "layout_id" for field in DocumentTemplate._meta.fields)

    if has_gallery_fields:
        for template in _gallery_templates():
            defaults = deepcopy(template)
            document_type = defaults.pop("document_type")
            layout_id = defaults.pop("layout_id")
            existing = DocumentTemplate.objects.filter(document_type=document_type, layout_id=layout_id).first()
            if existing is None:
                DocumentTemplate.objects.create(document_type=document_type, layout_id=layout_id, **defaults)
                created_count += 1
                continue

            legacy = LEGACY_DEFAULT_TEMPLATES.get(document_type)
            should_update_name = existing.name == defaults["name"] or (
                layout_id == "modern_corporate" and legacy and _matches_legacy_default(existing, legacy)
            )
            update_fields = [
                "description",
                "required_fields",
                "body",
                "theme",
                "header_style",
                "footer_style",
                "font",
                "color_scheme",
                "is_active",
                "updated_at",
            ]
            if should_update_name:
                existing.name = defaults["name"]
                update_fields.insert(0, "name")
            for field in update_fields:
                if field != "updated_at":
                    setattr(existing, field, defaults[field])
            existing.save(update_fields=update_fields)

        return created_count

    for template in DEFAULT_TEMPLATES:
        template_defaults = {**deepcopy(template), "is_active": True}
        document_type = template["document_type"]
        existing = DocumentTemplate.objects.filter(document_type=document_type).first()
        if existing is None:
            DocumentTemplate.objects.create(**template_defaults)
            created_count += 1
            continue

        legacy = LEGACY_DEFAULT_TEMPLATES.get(document_type)
        if legacy and _matches_legacy_default(existing, legacy):
            for field, value in template_defaults.items():
                setattr(existing, field, value)
            existing.save(update_fields=["name", "description", "required_fields", "body", "is_active", "updated_at"])

    return created_count

# AI-Powered Legal Document Platform

Production-oriented MVP for generating, managing, editing, comparing, analyzing, and exporting legal documents.

## Stack

- Backend: Django, Django REST Framework, JWT, PostgreSQL, ReportLab, Gemini API
- Frontend: React, TypeScript, Vite
- AI: provider abstraction with a Gemini implementation

## Backend Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Update `.env` with your PostgreSQL `DATABASE_URL` and `GEMINI_API_KEY`.

For local development without PostgreSQL, remove or leave `DATABASE_URL` unset to use SQLite.

```powershell
python manage.py migrate
python manage.py seed_legal_templates
python manage.py runserver
```

AI configuration defaults to `AI_PROVIDER=gemini` and `GEMINI_MODEL=gemini-2.5-flash`.

## Frontend Setup

```powershell
npm --prefix frontend install
npm run dev
```

The frontend runs on `http://127.0.0.1:5173` and proxies `/api` to Django on `http://127.0.0.1:8000`.

## API Overview

- `GET /api/legal/templates/`
- `GET /api/legal/documents/`
- `POST /api/legal/documents/`
- `GET /api/legal/documents/{id}/`
- `PUT /api/legal/documents/{id}/`
- `PATCH /api/legal/documents/{id}/`
- `DELETE /api/legal/documents/{id}/`
- `POST /api/legal/documents/generate/`
- `POST /api/legal/documents/{id}/explain-clause/`
- `POST /api/legal/documents/{id}/analyze-risks/`
- `POST /api/legal/documents/{id}/compare/`
- `GET /api/legal/documents/{id}/download-pdf/`

## Versioning

Every document create stores version 1. Any update that changes `content` creates the next `DocumentVersion` while preserving the previous versions.

## Verification

```powershell
python manage.py test apps.legal
npm run build
npm run lint
```

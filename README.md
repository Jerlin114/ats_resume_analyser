# ResumeIQ – AI Resume Analyzer

![Django](https://img.shields.io/badge/Django-4.2+-092e20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-CDN-38bdf8?style=for-the-badge&logo=tailwind-css&logoColor=white)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-In--Memory_Extraction-dc2626?style=for-the-badge)
![Status](https://img.shields.io/badge/Tests-13%2F13%20Passing-success?style=for-the-badge)

**ResumeIQ** is a modern SaaS-style web application built with Python and Django that evaluates candidate PDF resumes against target job descriptions using PyMuPDF and an LLM API. It generates instant qualification match scores, identifies key matching skills and skill gaps, and provides tailored, actionable recommendations to optimize resumes for target roles.

---

## ✨ Features

- **Professional SaaS Dashboard**: Clean, responsive layout crafted with Tailwind CSS (via CDN) and vanilla JavaScript.
- **In-Memory PDF Text Extraction**: Uses **PyMuPDF (`fitz`)** to parse PDF text layers in volatile RAM without ever writing files to the disk.
- **Strict Privacy & Zero Retention**:
  - Resumes are processed strictly in-memory.
  - No resume files are saved to permanent storage or databases.
  - Resume contents are never written to application logs.
- **Flexible AI Integration**:
  - **Google Gemini API** (recommended, e.g. `gemini-1.5-flash`).
  - **OpenAI & OpenAI-Compatible APIs** (e.g. `gpt-4o-mini`, Groq, OpenRouter, Ollama).
  - **Intelligent Heuristic Fallback Engine**: Works completely offline out of the box even before API keys are configured, ensuring 100% testability.
- **Structured Evaluation Output**:
  - **Estimated Resume-Job Match Score (0–100%)** displayed in an animated circular progress gauge.
  - **Prominent Disclaimer**: Clearly labels match scores as *AI-generated estimates*, not official ATS scores.
  - **Matching Skills**: Highlighted with emerald badges and checkmarks.
  - **Missing Skills & Gaps**: Clearly flagged with alert badges.
  - **Actionable Improvement Suggestions**: Numbered, high-impact recommendations to improve interview callback rates.
  - **Overall Executive Assessment**: Concise summary of candidate alignment.
- **Robust Validation**: Enforces maximum 5 MB file size limit, `.pdf` extension check, and `%PDF-` magic byte inspection.
- **One-Click Demo Testing**: Includes quick-load sample job descriptions (Python Full-Stack, Frontend Engineer, AI/ML Engineer).
- **Report Export**: Copy summary directly to clipboard or print/save as clean PDF.
- **100% Automated Test Coverage**: Built-in Django test suite verifying file validation, extraction, AI schemas, and API endpoints.

---

## 🛠 Tech Stack

| Component | Technology | Description |
|---|---|---|
| **Backend** | Python 3.10+, Django 4.2+ | Lightweight MTV architecture, zero complex DB models |
| **PDF Extraction** | PyMuPDF (`fitz` / `pymupdf`) | High-speed, in-memory stream text extraction |
| **Frontend** | HTML5, Tailwind CSS (CDN), Vanilla JS | Responsive, animated SaaS interface, no React or npm build steps |
| **Database** | SQLite | Lightweight zero-configuration local database |
| **AI / LLM** | Google Gemini / OpenAI / Fallback Engine | REST JSON API integration with structured prompt schemas |
| **Environment** | `python-dotenv` | Secure environment variable management |

---

## 📁 Project Structure

```text
projdoc/
├── manage.py                     # Django management script
├── requirements.txt              # Core project dependencies
├── .env.example                  # Environment configuration template
├── .env                          # Local environment variables (git-ignored)
├── .gitignore                    # Git ignore file
├── db.sqlite3                    # SQLite database
├── resumeiq/                     # Django project configuration
│   ├── __init__.py
│   ├── settings.py               # Settings with 5MB in-memory upload limits
│   ├── urls.py                   # Root URL dispatcher
│   ├── wsgi.py                   # WSGI deployment entry point
│   └── asgi.py                   # ASGI deployment entry point
└── analyzer/                     # Core ResumeIQ application
    ├── __init__.py
    ├── apps.py                   # App configuration
    ├── forms.py                  # ResumeAnalysisForm with strict PDF validation
    ├── views.py                  # Dashboard, analyze API, sample jobs views
    ├── urls.py                   # App URL routing
    ├── tests.py                  # 13 comprehensive automated unit & integration tests
    ├── services/
    │   ├── __init__.py
    │   ├── pdf_service.py        # PyMuPDF in-memory text extractor
    │   └── ai_service.py         # Multi-provider LLM client & heuristic engine
    ├── static/
    │   └── analyzer/
    │       ├── css/
    │       │   └── custom.css    # Circular gauge animations & print styles
    │       └── js/
    │           └── dashboard.js  # Drag-and-drop, AJAX requests, DOM renderer
    └── templates/
        └── analyzer/
            ├── base.html         # Tailwind CDN, navigation, privacy footer
            └── dashboard.html    # SaaS dashboard, dropzone, metrics & cards
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10 or higher
- `pip` package manager

### 2. Setup Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` to configure your preferred LLM provider:

```dotenv
DJANGO_SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Maximum upload limit in Megabytes (default: 5)
MAX_UPLOAD_SIZE_MB=5

# LLM Provider: 'auto', 'gemini', 'openai', or 'mock'
LLM_PROVIDER=auto

# Option A: Google Gemini API (Recommended)
GEMINI_API_KEY=your_actual_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash

# Option B: OpenAI API (or compatible e.g. Groq / OpenRouter)
OPENAI_API_KEY=your_actual_openai_api_key
OPENAI_MODEL=gpt-4o-mini
```

> **Note**: If neither API key is provided, ResumeIQ automatically runs in **Intelligent Heuristic Mode**, analyzing keywords and computing real qualification overlaps so you can test and demonstrate the app immediately without waiting for API keys!

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Start Development Server

```bash
python manage.py runserver
```

Open your browser and navigate to:
**`http://127.0.0.1:8000/`**

---

## 🧪 Running Automated Tests

Run the complete test suite with:

```bash
python manage.py test
```

### Test Coverage Highlights
- ✅ **PDF In-Memory Extraction**: Extracts text without saving to disk.
- ✅ **PDF Header Validation**: Rejects files missing `%PDF-` magic bytes.
- ✅ **Size Limit Enforcement**: Rejects uploads exceeding 5 MB limit.
- ✅ **Empty File Rejection**: Rejects 0-byte files.
- ✅ **Form Validation**: Checks `.pdf` extension and minimum 30-character job description.
- ✅ **AI Service Output Schema**: Confirms `match_score`, `score_label`, `matching_skills`, `missing_skills`, `improvement_suggestions`, and `overall_assessment` conform to schema.
- ✅ **API Endpoints**: Tests `GET /`, `GET /api/sample-jobs/`, `POST /api/analyze/` error handling, and end-to-end success flows.

---

## 📡 API Reference

### `POST /api/analyze/`
Analyzes a PDF resume against a target job description.

- **Content-Type**: `multipart/form-data`
- **Fields**:
  - `resume_file` (File, required): PDF document (max 5 MB).
  - `job_description` (Text, required): Minimum 30 characters.
  - `csrfmiddlewaretoken` (Text, required).

#### Example Response (HTTP 200):
```json
{
  "success": true,
  "data": {
    "match_score": 82,
    "score_label": "AI-generated estimate (Not an official ATS score)",
    "matching_skills": ["Python", "Django", "REST APIs", "PostgreSQL", "Git"],
    "missing_skills": ["Docker", "Kubernetes", "AWS"],
    "improvement_suggestions": [
      "Quantify your accomplishments using measurable KPIs (e.g., 'improved system performance by 25%').",
      "Incorporate missing core competencies prominently: emphasize experience with Docker, Kubernetes.",
      "Move evidence of your matching expertise in Python, Django to the top third of your resume."
    ],
    "overall_assessment": "Strong Match: The candidate's profile strongly aligns with the target role, matching 5 key technical requirements.",
    "meta": {
      "provider": "Gemini (gemini-1.5-flash)",
      "mode": "live_llm"
    }
  }
}
```

#### Example Error Response (HTTP 400):
```json
{
  "success": false,
  "error": "File size exceeds 5 MB limit."
}
```

---

## 🔒 Privacy & Security Policy

1. **Zero Permanent Storage**: Resumes are held solely in temporary Python process memory (`io.BytesIO`) during text extraction.
2. **Immediate Memory Disposal**: File buffers and PyMuPDF document handles are explicitly closed and released from RAM immediately after parsing.
3. **No Content Logging**: Resume text and personal identifying information (PII) are never written to Django logs or console output.
4. **Header Verification**: Uploaded files must match PDF magic signature bytes (`%PDF-`) to prevent arbitrary file upload vulnerabilities.
5. **Configurable Limits**: Upload limits are enforced at both frontend (JavaScript) and backend (Django form + service layer).

---

## 📄 License
MIT License. Built for developers and job seekers.

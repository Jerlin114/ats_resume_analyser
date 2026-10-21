"""
Views for ResumeIQ – AI Resume Analyzer.
Provides dashboard presentation and secure memory-only resume analysis endpoints.
"""

import json
import logging
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .forms import ResumeAnalysisForm
from .services.pdf_service import extract_text_from_pdf, PDFExtractionError
from .services.ai_service import analyze_resume_against_job

logger = logging.getLogger(__name__)

SAMPLE_JOB_DESCRIPTIONS = {
    "django_developer": {
        "title": "Senior Python & Django Full-Stack Developer",
        "description": (
            "We are seeking an experienced Senior Python / Django Developer to build robust SaaS applications.\n\n"
            "Responsibilities:\n"
            "- Design, develop, and maintain high-volume web applications using Python 3 and Django.\n"
            "- Build clean RESTful APIs and microservices with Django REST Framework.\n"
            "- Collaborate with frontend teams utilizing Tailwind CSS, JavaScript, and HTML5.\n"
            "- Manage relational databases (PostgreSQL, SQLite) and caching mechanisms (Redis).\n"
            "- Implement automated testing (pytest, Django TestCase) and CI/CD pipelines.\n"
            "- Deploy applications using Docker, Kubernetes, and AWS cloud infrastructure.\n\n"
            "Requirements:\n"
            "- 4+ years of professional backend experience with Python and Django.\n"
            "- Strong grasp of SQL, ORM optimization, and database migrations.\n"
            "- Familiarity with containerization (Docker) and Git version control.\n"
            "- Experience integrating third-party APIs (LLMs, payment gateways, authentication).\n"
            "- Excellent problem-solving, code review, and collaborative communication skills."
        )
    },
    "frontend_engineer": {
        "title": "Frontend Engineer (JavaScript / Tailwind CSS)",
        "description": (
            "Looking for a creative and detail-oriented Frontend Engineer.\n\n"
            "Key Requirements:\n"
            "- 3+ years modern JavaScript (ES6+), HTML5, and responsive CSS with Tailwind CSS.\n"
            "- Experience with single-page applications, UI state management, and REST APIs.\n"
            "- Deep understanding of web accessibility (WCAG), performance optimization, and cross-browser quirks.\n"
            "- Git workflow, automated UI testing, and Figma design implementation."
        )
    },
    "ai_ml_engineer": {
        "title": "AI / ML Applications Engineer",
        "description": (
            "Seeking an AI Application Engineer to integrate modern LLM capabilities into enterprise workflows.\n\n"
            "Requirements:\n"
            "- Strong Python skills with FastAPI / Flask / Django.\n"
            "- Hands-on experience with LLM APIs (OpenAI, Google Gemini, Anthropic), prompt engineering, and RAG architectures.\n"
            "- Vector databases (Pinecone, Chroma, pgvector) and embedding pipelines.\n"
            "- PyTorch, HuggingFace transformers, and evaluation metrics for generative models."
        )
    }
}


@require_http_methods(["GET"])
def dashboard_view(request):
    """Render the SaaS dashboard for ResumeIQ."""
    form = ResumeAnalysisForm()
    max_mb = getattr(settings, 'MAX_UPLOAD_SIZE_MB', 5)
    return render(
        request,
        'analyzer/dashboard.html',
        {
            'form': form,
            'max_size_mb': max_mb,
            'sample_jobs': SAMPLE_JOB_DESCRIPTIONS,
        }
    )


@require_POST
def analyze_resume_api(request):
    """
    AJAX endpoint for resume analysis.
    Validates PDF in-memory, extracts text via PyMuPDF, invokes LLM service,
    and returns structured evaluation JSON.
    Guarantees NO permanent storage or logging of resume data.
    """
    form = ResumeAnalysisForm(request.POST, request.FILES)

    if not form.is_valid():
        # Collect first validation error message
        errors = []
        for field, error_list in form.errors.items():
            for err in error_list:
                errors.append(f"{err}")
        error_msg = " | ".join(errors) if errors else "Invalid input provided."
        return JsonResponse({
            "success": False,
            "error": error_msg
        }, status=400)

    uploaded_pdf = form.cleaned_data['resume_file']
    job_description = form.cleaned_data['job_description']

    try:
        # 1. In-memory text extraction using PyMuPDF (fitz)
        max_mb = getattr(settings, 'MAX_UPLOAD_SIZE_MB', 5)
        resume_text = extract_text_from_pdf(uploaded_pdf, max_size_mb=max_mb)

        # 2. Invoke AI Service
        analysis_result = analyze_resume_against_job(resume_text, job_description)

        # 3. Return clean JSON response
        return JsonResponse({
            "success": True,
            "data": analysis_result
        }, status=200)

    except PDFExtractionError as exc:
        return JsonResponse({
            "success": False,
            "error": str(exc)
        }, status=400)
    except Exception as exc:
        logger.exception("Unexpected error occurred during resume analysis processing.")
        return JsonResponse({
            "success": False,
            "error": f"An unexpected error occurred while analyzing the resume: {str(exc)}"
        }, status=500)


@require_GET
def sample_jobs_api(request):
    """Returns sample job descriptions for quick testing."""
    return JsonResponse({
        "success": True,
        "samples": SAMPLE_JOB_DESCRIPTIONS
    })

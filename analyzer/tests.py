"""
Automated Test Suite for ResumeIQ – AI Resume Analyzer.

Covers:
1. PyMuPDF in-memory text extraction and validation.
2. File type and 5 MB size limit enforcement.
3. Form validation.
4. AI service schema, scoring, and fallback handling.
5. End-to-end API integration tests.
"""

import io
from unittest.mock import patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from analyzer.forms import ResumeAnalysisForm
from analyzer.services.pdf_service import extract_text_from_pdf, PDFExtractionError
from analyzer.services.ai_service import analyze_resume_against_job, _clean_json_response, _heuristic_analyzer


def create_sample_pdf_bytes(text_content: str = "Jane Doe\nSenior Python Developer\nSkills: Python, Django, REST APIs, Git, PostgreSQL") -> bytes:
    """Helper to generate a valid in-memory PDF byte stream using PyMuPDF."""
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), text_content, fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


class PDFExtractionTestCase(TestCase):
    """Test PDF text extraction, validation, and privacy constraints."""

    def test_extract_valid_pdf_text(self):
        """Valid PDF text should be extracted accurately without disk persistence."""
        expected_text = "John Smith\nFull-Stack Engineer\nExperienced with Python, Django, Tailwind CSS"
        pdf_bytes = create_sample_pdf_bytes(expected_text)
        file_obj = io.BytesIO(pdf_bytes)

        extracted = extract_text_from_pdf(file_obj, max_size_mb=5)
        self.assertIn("Python", extracted)
        self.assertIn("Django", extracted)
        self.assertIn("John Smith", extracted)

    def test_reject_non_pdf_file(self):
        """Files without %PDF- magic signature must be rejected."""
        fake_file = io.BytesIO(b"Hello world, this is a plain text file, not a PDF.")
        with self.assertRaises(PDFExtractionError) as ctx:
            extract_text_from_pdf(fake_file, max_size_mb=5)
        self.assertIn("not a valid PDF", str(ctx.exception))

    def test_reject_oversized_file(self):
        """Files exceeding max_size_mb (5 MB) must be rejected."""
        # Create a dummy stream larger than 1MB when max is 1MB
        large_bytes = b"%PDF-" + (b"A" * (2 * 1024 * 1024))
        file_obj = io.BytesIO(large_bytes)
        with self.assertRaises(PDFExtractionError) as ctx:
            extract_text_from_pdf(file_obj, max_size_mb=1)
        self.assertIn("exceeds the limit", str(ctx.exception))

    def test_reject_empty_file(self):
        """Empty files (0 bytes) must be rejected."""
        empty_file = io.BytesIO(b"")
        with self.assertRaises(PDFExtractionError) as ctx:
            extract_text_from_pdf(empty_file, max_size_mb=5)
        self.assertIn("empty", str(ctx.exception).lower())


class AIServiceTestCase(TestCase):
    """Test AI Service structured output, score calculations, and schema integrity."""

    def test_heuristic_analyzer_schema(self):
        """Verify the structured response matches all project requirements."""
        resume = "Senior Python Developer with 5 years experience in Django, REST APIs, SQL, and Git."
        jd = "Seeking a Senior Python / Django Developer with experience in Docker, Kubernetes, CI/CD, and Git."

        result = analyze_resume_against_job(resume, jd)

        # Check required fields from specifications
        self.assertIn("match_score", result)
        self.assertIsInstance(result["match_score"], int)
        self.assertTrue(0 <= result["match_score"] <= 100)

        self.assertIn("score_label", result)
        self.assertIn("AI-generated estimate", result["score_label"])

        self.assertIn("matching_skills", result)
        self.assertIsInstance(result["matching_skills"], list)
        self.assertIn("Python", result["matching_skills"])
        self.assertIn("Django", result["matching_skills"])

        self.assertIn("missing_skills", result)
        self.assertIsInstance(result["missing_skills"], list)

        self.assertIn("improvement_suggestions", result)
        self.assertIsInstance(result["improvement_suggestions"], list)
        self.assertTrue(len(result["improvement_suggestions"]) > 0)

        self.assertIn("overall_assessment", result)
        self.assertIsInstance(result["overall_assessment"], str)
        self.assertTrue(len(result["overall_assessment"]) > 20)

    def test_clean_json_response_with_fencing(self):
        """Verify markdown fenced JSON strings are parsed cleanly."""
        raw = '```json\n{"match_score": 88, "matching_skills": ["Python"]}\n```'
        parsed = _clean_json_response(raw)
        self.assertEqual(parsed["match_score"], 88)
        self.assertEqual(parsed["matching_skills"], ["Python"])


class ResumeAnalysisFormTestCase(TestCase):
    """Test form validations for file type, file size, and job description length."""

    def test_valid_form_submission(self):
        """Valid PDF and adequate JD length should pass validation."""
        pdf_bytes = create_sample_pdf_bytes("Alice Engineer\nPython Django Specialist")
        upload = SimpleUploadedFile("alice_resume.pdf", pdf_bytes, content_type="application/pdf")
        jd = "We are hiring a backend developer experienced with Python, Django, and database management."

        form = ResumeAnalysisForm(data={"job_description": jd}, files={"resume_file": upload})
        self.assertTrue(form.is_valid(), form.errors)

    def test_reject_invalid_extension(self):
        """Non-pdf extension should fail form validation."""
        upload = SimpleUploadedFile("resume.docx", b"%PDF-dummy", content_type="application/msword")
        jd = "A valid job description that is long enough to pass minimum length criteria."

        form = ResumeAnalysisForm(data={"job_description": jd}, files={"resume_file": upload})
        self.assertFalse(form.is_valid())
        self.assertIn("resume_file", form.errors)

    def test_reject_short_job_description(self):
        """Job description under 30 characters must be rejected."""
        pdf_bytes = create_sample_pdf_bytes("Bob Programmer")
        upload = SimpleUploadedFile("bob_resume.pdf", pdf_bytes, content_type="application/pdf")

        form = ResumeAnalysisForm(data={"job_description": "Short JD"}, files={"resume_file": upload})
        self.assertFalse(form.is_valid())
        self.assertIn("job_description", form.errors)


class ViewsIntegrationTestCase(TestCase):
    """Test HTTP endpoints, dashboard rendering, and AJAX API."""

    def setUp(self):
        self.client = Client()

    def test_dashboard_view_renders(self):
        """GET / should render the dashboard page with status 200."""
        response = self.client.get(reverse('analyzer:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ResumeIQ")
        self.assertContains(response, "AI Resume Analyzer")
        self.assertContains(response, "Upload Resume")

    def test_sample_jobs_api(self):
        """GET /api/sample-jobs/ should return sample job data."""
        response = self.client.get(reverse('analyzer:sample_jobs'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("django_developer", data.get("samples", {}))

    def test_analyze_api_missing_file_returns_400(self):
        """POST /api/analyze/ without a file must return HTTP 400."""
        response = self.client.post(
            reverse('analyzer:analyze_resume'),
            {"job_description": "Valid job description exceeding 30 characters for testing purposes."}
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data.get("success"))
        self.assertIn("error", data)

    def test_analyze_api_success_flow(self):
        """POST /api/analyze/ with valid PDF and JD returns structured JSON."""
        pdf_bytes = create_sample_pdf_bytes(
            "David Chen\nSenior Backend Engineer\nSkills: Python, Django, REST APIs, PostgreSQL, Git, Redis"
        )
        upload = SimpleUploadedFile("david_resume.pdf", pdf_bytes, content_type="application/pdf")
        jd = (
            "Looking for a Senior Python Developer with strong Django, REST APIs, Docker, "
            "and Kubernetes experience to join our core backend engineering team."
        )

        response = self.client.post(
            reverse('analyzer:analyze_resume'),
            {
                "resume_file": upload,
                "job_description": jd
            }
        )

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data.get("success"))

        result = json_data.get("data", {})
        self.assertIn("match_score", result)
        self.assertIn("score_label", result)
        self.assertIn("matching_skills", result)
        self.assertIn("missing_skills", result)
        self.assertIn("improvement_suggestions", result)
        self.assertIn("overall_assessment", result)

        # Check skills detected
        self.assertIn("Python", result["matching_skills"])
        self.assertIn("Django", result["matching_skills"])
        self.assertIn("Docker", result["missing_skills"])

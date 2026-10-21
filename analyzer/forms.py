"""
Django Forms for ResumeIQ.
Provides strict validation for PDF uploads and Job Description text.
"""

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError


class ResumeAnalysisForm(forms.Form):
    """
    Form for validating resume PDF upload and target job description.
    Enforces maximum 5 MB limit, PDF extension, and PDF header magic bytes.
    """

    resume_file = forms.FileField(
        required=True,
        label="Upload Resume (PDF)",
        help_text="Upload your resume in PDF format (maximum 5 MB).",
        widget=forms.FileInput(
            attrs={
                "id": "resume-file-input",
                "accept": ".pdf,application/pdf",
                "class": "sr-only",
            }
        ),
    )

    job_description = forms.CharField(
        required=True,
        label="Job Description",
        min_length=30,
        max_length=20000,
        help_text="Paste the target job description or requirements.",
        widget=forms.Textarea(
            attrs={
                "id": "job-description-input",
                "rows": 8,
                "placeholder": "Paste the complete job description, key responsibilities, and required qualifications here...",
                "class": (
                    "w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 "
                    "bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 "
                    "focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent "
                    "transition duration-200 resize-y text-sm leading-relaxed"
                ),
            }
        ),
    )

    def clean_resume_file(self):
        uploaded = self.cleaned_data.get("resume_file")
        if not uploaded:
            raise ValidationError("Please select a PDF resume file to upload.")

        # 1. Filename extension validation
        filename = uploaded.name.lower()
        if not filename.endswith(".pdf"):
            raise ValidationError("Only PDF files (.pdf) are allowed. Please upload a valid PDF.")

        # 2. File size validation (<= 5 MB)
        max_mb = getattr(settings, "MAX_UPLOAD_SIZE_MB", 5)
        max_bytes = max_mb * 1024 * 1024
        if uploaded.size > max_bytes:
            raise ValidationError(
                f"File size exceeds {max_mb} MB limit (uploaded size: {uploaded.size / (1024 * 1024):.2f} MB)."
            )

        if uploaded.size == 0:
            raise ValidationError("The uploaded file is empty (0 bytes).")

        # 3. Magic byte signature check (%PDF-)
        try:
            sample = uploaded.read(1024)
            uploaded.seek(0)
            if not sample.startswith(b"%PDF-"):
                raise ValidationError("The uploaded file does not appear to be a valid PDF document.")
        except ValidationError:
            raise
        except Exception as exc:
            raise ValidationError(f"Error inspecting file header: {str(exc)}")

        return uploaded

    def clean_job_description(self):
        jd = self.cleaned_data.get("job_description", "").strip()
        if len(jd) < 30:
            raise ValidationError(
                "Please provide a more detailed job description (minimum 30 characters) for accurate matching."
            )
        return jd

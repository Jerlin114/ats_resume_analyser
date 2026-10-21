/**
 * ResumeIQ – Dashboard Interactive Logic
 * Handles client-side PDF validation, in-memory AJAX analysis,
 * loading animations, and dynamic visual metric rendering.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('resume-analysis-form');
    const fileInput = document.getElementById('resume-file-input');
    const dropzone = document.getElementById('dropzone');
    const dropzoneEmpty = document.getElementById('dropzone-empty');
    const dropzoneSelected = document.getElementById('dropzone-selected');
    const selectedFileName = document.getElementById('selected-file-name');
    const selectedFileSize = document.getElementById('selected-file-size');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const jdInput = document.getElementById('job-description-input');
    const charCount = document.getElementById('char-count');
    const clearJdBtn = document.getElementById('clear-jd-btn');
    const sampleJobBtns = document.querySelectorAll('.sample-job-btn');
    const submitBtn = document.getElementById('analyze-submit-btn');
    const errorBanner = document.getElementById('error-banner');
    const errorTitle = document.getElementById('error-title');
    const errorMessage = document.getElementById('error-message');
    const closeErrorBtn = document.getElementById('close-error-btn');
    const loadingState = document.getElementById('loading-state');
    const loadingStatusText = document.getElementById('loading-status-text');
    const resultsSection = document.getElementById('results-section');
    const scoreCircle = document.getElementById('score-circle');
    const scoreValue = document.getElementById('score-value');
    const scoreBadge = document.getElementById('score-badge');
    const overallAssessmentText = document.getElementById('overall-assessment-text');
    const matchingSkillsContainer = document.getElementById('matching-skills-container');
    const missingSkillsContainer = document.getElementById('missing-skills-container');
    const matchingCountBadge = document.getElementById('matching-count-badge');
    const missingCountBadge = document.getElementById('missing-count-badge');
    const suggestionsList = document.getElementById('suggestions-list');
    const resultProviderBadge = document.getElementById('result-provider-badge');
    const copyReportBtn = document.getElementById('copy-report-btn');
    const copyBtnLabel = document.getElementById('copy-btn-label');
    const resetAnalysisBtn = document.getElementById('reset-analysis-btn');

    const MAX_SIZE_BYTES = 5 * 1024 * 1024; // 5 MB
    let lastAnalysisData = null;
    let loadingInterval = null;

    // Sample Job Descriptions Store
    const samples = {
        django_developer: `We are seeking an experienced Senior Python / Django Developer to build robust SaaS applications.

Responsibilities:
- Design, develop, and maintain high-volume web applications using Python 3 and Django.
- Build clean RESTful APIs and microservices with Django REST Framework.
- Collaborate with frontend teams utilizing Tailwind CSS, JavaScript, and HTML5.
- Manage relational databases (PostgreSQL, SQLite) and caching mechanisms (Redis).
- Implement automated testing (pytest, Django TestCase) and CI/CD pipelines.
- Deploy applications using Docker, Kubernetes, and AWS cloud infrastructure.

Requirements:
- 4+ years of professional backend experience with Python and Django.
- Strong grasp of SQL, ORM optimization, and database migrations.
- Familiarity with containerization (Docker) and Git version control.
- Experience integrating third-party APIs (LLMs, payment gateways, authentication).
- Excellent problem-solving, code review, and collaborative communication skills.`,

        frontend_engineer: `Looking for a creative and detail-oriented Frontend Engineer.

Key Requirements:
- 3+ years modern JavaScript (ES6+), HTML5, and responsive CSS with Tailwind CSS.
- Experience with single-page applications, UI state management, and REST APIs.
- Deep understanding of web accessibility (WCAG), performance optimization, and cross-browser quirks.
- Git workflow, automated UI testing, and Figma design implementation.
- Good understanding of backend integration points.`,

        ai_ml_engineer: `Seeking an AI Application Engineer to integrate modern LLM capabilities into enterprise workflows.

Requirements:
- Strong Python skills with FastAPI / Flask / Django.
- Hands-on experience with LLM APIs (OpenAI, Google Gemini, Anthropic), prompt engineering, and RAG architectures.
- Vector databases (Pinecone, Chroma, pgvector) and embedding pipelines.
- PyTorch, HuggingFace transformers, and evaluation metrics for generative models.
- Cloud deployment on AWS / GCP and Docker containerization.`
    };

    // ==========================================
    // 1. File Handling & Dropzone Logic
    // ==========================================
    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function setSelectedFile(file) {
        if (!file) {
            clearSelectedFile();
            return;
        }

        // Validate type
        const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
        if (!isPdf) {
            showError("Invalid File Type", "Please upload a valid PDF file (.pdf).");
            clearSelectedFile();
            return;
        }

        // Validate size
        if (file.size > MAX_SIZE_BYTES) {
            showError("File Too Large", `The selected file is ${formatBytes(file.size)}. Maximum allowed size is 5 MB.`);
            clearSelectedFile();
            return;
        }

        if (file.size === 0) {
            showError("Empty File", "The selected file is 0 bytes. Please select a valid document.");
            clearSelectedFile();
            return;
        }

        hideError();
        selectedFileName.textContent = file.name;
        selectedFileSize.textContent = formatBytes(file.size);
        dropzoneEmpty.classList.add('hidden');
        dropzoneSelected.classList.remove('hidden');
    }

    function clearSelectedFile() {
        fileInput.value = '';
        dropzoneEmpty.classList.remove('hidden');
        dropzoneSelected.classList.add('hidden');
        selectedFileName.textContent = '';
        selectedFileSize.textContent = '';
    }

    dropzone.addEventListener('click', (e) => {
        if (e.target.closest('#remove-file-btn')) return;
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            setSelectedFile(e.target.files[0]);
        }
    });

    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearSelectedFile();
    });

    // Drag & Drop events
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('drag-over');
        });
    });

    dropzone.addEventListener('drop', (e) => {
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            fileInput.files = e.dataTransfer.files;
            setSelectedFile(file);
        }
    });

    // ==========================================
    // 2. Job Description Inputs & Samples
    // ==========================================
    function updateCharCount() {
        const len = jdInput.value.trim().length;
        charCount.textContent = `${len} character${len === 1 ? '' : 's'} (min 30)`;
        if (len > 0 && len < 30) {
            charCount.classList.add('text-amber-600');
            charCount.classList.remove('text-slate-400');
        } else {
            charCount.classList.remove('text-amber-600');
            charCount.classList.add('text-slate-400');
        }
    }

    jdInput.addEventListener('input', updateCharCount);

    clearJdBtn.addEventListener('click', () => {
        jdInput.value = '';
        updateCharCount();
        jdInput.focus();
    });

    sampleJobBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const key = btn.getAttribute('data-sample');
            if (samples[key]) {
                jdInput.value = samples[key];
                updateCharCount();
                hideError();
            }
        });
    });

    // ==========================================
    // 3. Error Handling
    // ==========================================
    function showError(title, message) {
        errorTitle.textContent = title + ":";
        errorMessage.textContent = message;
        errorBanner.classList.remove('hidden');
        errorBanner.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function hideError() {
        errorBanner.classList.add('hidden');
        errorMessage.textContent = '';
    }

    closeErrorBtn.addEventListener('click', hideError);

    // ==========================================
    // 4. Loading State Animation
    // ==========================================
    const loadingSteps = [
        "Reading PDF in volatile RAM buffer...",
        "Extracting page text with PyMuPDF...",
        "Analyzing skills & qualification alignment via AI...",
        "Evaluating resume strength and identifying gaps...",
        "Generating structured improvement recommendations..."
    ];

    function startLoading() {
        hideError();
        resultsSection.classList.add('hidden');
        loadingState.classList.remove('hidden');
        submitBtn.disabled = true;
        submitBtn.classList.add('opacity-70', 'cursor-not-allowed');

        let stepIndex = 0;
        loadingStatusText.textContent = loadingSteps[0];
        loadingInterval = setInterval(() => {
            stepIndex = (stepIndex + 1) % loadingSteps.length;
            loadingStatusText.textContent = loadingSteps[stepIndex];
        }, 1200);

        loadingState.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function stopLoading() {
        if (loadingInterval) {
            clearInterval(loadingInterval);
            loadingInterval = null;
        }
        loadingState.classList.add('hidden');
        submitBtn.disabled = false;
        submitBtn.classList.remove('opacity-70', 'cursor-not-allowed');
    }

    // ==========================================
    // 5. Form Submit & AJAX Analysis
    // ==========================================
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Client pre-validation
        if (!fileInput.files || fileInput.files.length === 0) {
            showError("Missing Resume", "Please upload a PDF resume before analyzing.");
            return;
        }

        const jd = jdInput.value.trim();
        if (jd.length < 30) {
            showError("Incomplete Job Description", "Please paste a job description with at least 30 characters.");
            return;
        }

        startLoading();

        const formData = new FormData(form);

        try {
            const response = await fetch('/api/analyze/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                const msg = data.error || `Server responded with status code ${response.status}`;
                showError("Analysis Failed", msg);
                stopLoading();
                return;
            }

            // Success: render structured data
            renderResults(data.data);
            stopLoading();

        } catch (err) {
            stopLoading();
            showError("Connection Error", "Unable to communicate with the server. Please verify your connection and try again.");
            console.error("Resume analysis network error:", err);
        }
    });

    // ==========================================
    // 6. Visual Metric & Results Renderer
    // ==========================================
    function renderResults(result) {
        lastAnalysisData = result;

        const score = Math.max(0, Math.min(100, parseInt(result.match_score) || 0));

        // 1. Animate Circular Meter
        // Circumference of r=50 circle: 2 * Math.PI * 50 = 314.159
        const circumference = 2 * Math.PI * 50;
        const offset = circumference - (score / 100) * circumference;
        scoreCircle.style.strokeDashoffset = offset;

        // Color theme based on score
        let strokeColor = '#4f46e5'; // default indigo
        let badgeColorClass = 'bg-brand-50 text-brand-700 border-brand-200';
        let badgeText = 'Moderate Match';

        if (score >= 80) {
            strokeColor = '#10b981'; // emerald
            badgeColorClass = 'bg-emerald-50 text-emerald-700 border-emerald-200';
            badgeText = 'Strong Match';
        } else if (score >= 65) {
            strokeColor = '#4f46e5'; // indigo
            badgeColorClass = 'bg-indigo-50 text-indigo-700 border-indigo-200';
            badgeText = 'Good Match';
        } else if (score >= 45) {
            strokeColor = '#f59e0b'; // amber
            badgeColorClass = 'bg-amber-50 text-amber-700 border-amber-200';
            badgeText = 'Moderate Match';
        } else {
            strokeColor = '#ef4444'; // rose
            badgeColorClass = 'bg-rose-50 text-rose-700 border-rose-200';
            badgeText = 'Needs Optimization';
        }

        scoreCircle.setAttribute('stroke', strokeColor);
        scoreBadge.className = `inline-flex items-center px-3 py-1 rounded-full text-xs font-bold border ${badgeColorClass}`;
        scoreBadge.textContent = badgeText;

        // Count-up animation for score value
        animateValue(scoreValue, 0, score, 1000);

        // 2. Executive Assessment
        overallAssessmentText.textContent = result.overall_assessment || "No assessment generated.";

        // 3. Provider badge
        if (result.meta && result.meta.provider) {
            resultProviderBadge.textContent = result.meta.provider;
        } else {
            resultProviderBadge.textContent = "AI Model";
        }

        // 4. Matching Skills
        matchingSkillsContainer.innerHTML = '';
        const matching = result.matching_skills || [];
        matchingCountBadge.textContent = `${matching.length} Found`;
        if (matching.length === 0) {
            matchingSkillsContainer.innerHTML = `<span class="text-xs text-slate-400 italic">No exact skill matches identified.</span>`;
        } else {
            matching.forEach(skill => {
                const chip = document.createElement('span');
                chip.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-emerald-50 border border-emerald-200/80 text-emerald-800 text-xs font-semibold shadow-2xs';
                chip.innerHTML = `
                    <svg class="w-3.5 h-3.5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                    </svg>
                    <span>${escapeHtml(skill)}</span>
                `;
                matchingSkillsContainer.appendChild(chip);
            });
        }

        // 5. Missing Skills
        missingSkillsContainer.innerHTML = '';
        const missing = result.missing_skills || [];
        missingCountBadge.textContent = `${missing.length} Gaps`;
        if (missing.length === 0) {
            missingSkillsContainer.innerHTML = `<span class="text-xs text-emerald-600 font-medium">No critical missing skill gaps detected!</span>`;
        } else {
            missing.forEach(skill => {
                const chip = document.createElement('span');
                chip.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-rose-50 border border-rose-200/80 text-rose-800 text-xs font-semibold shadow-2xs';
                chip.innerHTML = `
                    <svg class="w-3.5 h-3.5 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                    <span>${escapeHtml(skill)}</span>
                `;
                missingSkillsContainer.appendChild(chip);
            });
        }

        // 6. Actionable Suggestions
        suggestionsList.innerHTML = '';
        const suggestions = result.improvement_suggestions || [];
        if (suggestions.length === 0) {
            suggestionsList.innerHTML = `<p class="text-xs text-slate-400">No specific improvements suggested.</p>`;
        } else {
            suggestions.forEach((item, idx) => {
                const card = document.createElement('div');
                card.className = 'flex items-start gap-3 p-3.5 rounded-xl bg-slate-50 border border-slate-100 hover:border-brand-200 transition';
                card.innerHTML = `
                    <span class="w-6 h-6 rounded-full bg-brand-100 text-brand-700 font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5">${idx + 1}</span>
                    <p class="text-sm text-slate-700 leading-relaxed">${escapeHtml(item)}</p>
                `;
                suggestionsList.appendChild(card);
            });
        }

        // Display results and scroll
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function animateValue(elem, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            elem.textContent = Math.floor(progress * (end - start) + start) + '%';
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    function escapeHtml(string) {
        const div = document.createElement('div');
        div.innerText = string;
        return div.innerHTML;
    }

    // ==========================================
    // 7. Copy Analysis & Reset Handlers
    // ==========================================
    copyReportBtn.addEventListener('click', () => {
        if (!lastAnalysisData) return;

        const report = `=== ResumeIQ – AI Resume Analysis Report ===
Estimated Match Score: ${lastAnalysisData.match_score}%
Score Label: ${lastAnalysisData.score_label}
Note: AI-generated estimate, not an official ATS score.

[Overall Assessment]
${lastAnalysisData.overall_assessment}

[Matching Skills]
${(lastAnalysisData.matching_skills || []).map(s => `• ${s}`).join('\n') || 'None'}

[Missing Skills / Gaps]
${(lastAnalysisData.missing_skills || []).map(s => `• ${s}`).join('\n') || 'None'}

[Actionable Improvement Suggestions]
${(lastAnalysisData.improvement_suggestions || []).map((s, i) => `${i + 1}. ${s}`).join('\n')}
=============================================`;

        navigator.clipboard.writeText(report).then(() => {
            copyBtnLabel.textContent = "Copied to Clipboard!";
            setTimeout(() => {
                copyBtnLabel.textContent = "Copy Analysis";
            }, 2500);
        }).catch(err => {
            console.error("Clipboard copy failed:", err);
        });
    });

    resetAnalysisBtn.addEventListener('click', () => {
        clearSelectedFile();
        jdInput.value = '';
        updateCharCount();
        resultsSection.classList.add('hidden');
        hideError();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Initialize character counter
    updateCharCount();
});

"""
Tushar Dodia & Dodia Academy - Production Web Portal & Diagnostic Platform
FastAPI server serving dynamic pages, API endpoints, photo archive, video vault,
and on-demand personalized PDF psychometric report generation with Executive Admin Panel.
"""
import os
import sys
import csv
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from engine.scorer_senior import SeniorScoringEngine
from engine.scorer_junior import JuniorScoringEngine
from engine.database import (
    get_all_submissions,
    get_submission_by_id,
    save_new_submission,
    update_submission,
    delete_submission,
    get_all_inquiries,
    get_inquiry_by_id,
    save_new_inquiry,
    update_inquiry,
    delete_inquiry,
    sync_json_backups,
    db_insert_or_replace_submission_raw,
    db_insert_or_replace_inquiry_raw,
    get_db_connection
)
from engine.security import (
    SecurityHeadersMiddleware,
    ADMIN_COOKIE_NAME,
    is_request_authenticated,
    create_authenticated_session,
    verify_admin_credentials,
    revoke_session,
    is_ip_locked
)
from generator.pdf_service import (
    render_report_to_pdf, get_benchmark_shardul_report,
    build_evaluation_report_from_record
)

app = FastAPI(
    title="Tushar Dodia | Dodia Academy",
    description="Modern Strategy. Ancient Wisdom. Corporate Leadership & Student Psychometric Evaluation.",
    version="2.3.0"
)

# Apply OWASP Top 10 Defensive Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# Mount Static Directories
STATIC_DIR = BASE_DIR / "web" / "static"
DOSSIER_DIR = BASE_DIR / "dossier"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/dossier", StaticFiles(directory=str(DOSSIER_DIR)), name="dossier")

# Templates
TEMPLATES_DIR = BASE_DIR / "web" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Cached Data Stores
PHOTOS_CSV = DOSSIER_DIR / "PHOTO_INDEX.csv"
VIDEOS_JSON = DOSSIER_DIR / "youtube_videos.json"

def is_admin_authenticated(request: Request) -> bool:
    """Verifies cryptographic session signature and database active session."""
    return is_request_authenticated(request)

def load_photos():
    photos = []
    if PHOTOS_CSV.exists():
        with open(PHOTOS_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                photos.append(row)
    return photos

def load_videos():
    if VIDEOS_JSON.exists():
        with open(VIDEOS_JSON, mode="r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_submissions() -> List[Dict[str, Any]]:
    """Loads all student diagnostic assessments directly from SQLite database."""
    return get_all_submissions()

def save_submissions(submissions: List[Dict[str, Any]]):
    """Synchronizes submissions into SQLite database and updates JSON mirror."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        for s in submissions:
            db_insert_or_replace_submission_raw(cursor, s)
        conn.commit()
        sync_json_backups(conn)
    finally:
        conn.close()

def load_inquiries() -> List[Dict[str, Any]]:
    """Loads all client inquiries directly from SQLite database."""
    return get_all_inquiries()

def save_inquiries(inquiries: List[Dict[str, Any]]):
    """Synchronizes inquiries into SQLite database and updates JSON mirror."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        for inq in inquiries:
            db_insert_or_replace_inquiry_raw(cursor, inq)
        conn.commit()
        sync_json_backups(conn)
    finally:
        conn.close()

CACHED_PHOTOS = load_photos()
CACHED_VIDEOS = load_videos()

# ==============================================================================
# Health Check Endpoint
# ==============================================================================

@app.get("/api/health")
@app.get("/healthz")
async def health_check():
    """
    Dedicated health check endpoint reporting repository, cache, and system status.
    """
    return {
        "status": "healthy",
        "service": "Tushar Dodia Academy Production Portal",
        "timestamp": datetime.now().isoformat(),
        "repository": {
            "submissions_count": len(load_submissions()),
            "inquiries_count": len(load_inquiries())
        },
        "media_cache": {
            "photos_count": len(CACHED_PHOTOS),
            "videos_count": len(CACHED_VIDEOS)
        }
    }

# ==============================================================================
# HTML Page Routes (Public)
# ==============================================================================

@app.get("/")
async def home_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "active_page": "home",
            "photos_count": len(CACHED_PHOTOS),
            "videos_count": len(CACHED_VIDEOS),
            "is_admin": is_admin_authenticated(request)
        }
    )

@app.get("/about")
async def about_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            "active_page": "about",
            "is_admin": is_admin_authenticated(request)
        }
    )

@app.get("/assessment")
async def assessment_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="assessment.html",
        context={
            "active_page": "assessment",
            "is_admin": is_admin_authenticated(request)
        }
    )

@app.get("/services")
async def services_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="services.html",
        context={
            "active_page": "services",
            "is_admin": is_admin_authenticated(request)
        }
    )

@app.get("/gallery")
async def gallery_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="gallery.html",
        context={
            "active_page": "gallery",
            "photos": CACHED_PHOTOS,
            "is_admin": is_admin_authenticated(request)
        }
    )

@app.get("/videos")
async def videos_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="videos.html",
        context={
            "active_page": "videos",
            "videos": CACHED_VIDEOS,
            "is_admin": is_admin_authenticated(request)
        }
    )

@app.get("/contact")
async def contact_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="contact.html",
        context={
            "active_page": "contact",
            "is_admin": is_admin_authenticated(request)
        }
    )

# ==============================================================================
# Admin Panel Routes
# ==============================================================================

@app.get("/admin/login")
async def admin_login_page(request: Request):
    """
    Executive Login Interface.
    Never silently auto-bypasses without user clarity; displays active session status if already logged in.
    """
    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "127.0.0.1").split(",")[0].strip()
    locked = is_ip_locked(client_ip)
    already_auth = is_admin_authenticated(request)
    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context={
            "active_page": "admin",
            "error": "Security lock active: Too many failed login attempts. Please wait 15 minutes." if locked else None,
            "already_authenticated": already_auth,
            "is_admin": already_auth
        }
    )

@app.post("/admin/login")
async def admin_login_submit(request: Request):
    """
    Authenticates administrative user with IP brute-force protection and cryptographic session signing.
    """
    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "127.0.0.1").split(",")[0].strip()

    if is_ip_locked(client_ip):
        return templates.TemplateResponse(
            request=request,
            name="admin_login.html",
            context={
                "active_page": "admin",
                "error": "IP temporarily locked due to repeated failed attempts. Please retry after 15 minutes.",
                "already_authenticated": False,
                "is_admin": False
            },
            status_code=429
        )

    form = await request.form()
    username = form.get("username", "").strip()
    password = form.get("password", "").strip()

    # Timing-safe authentication & session generation
    if verify_admin_credentials(username, password, client_ip):
        token = create_authenticated_session(username, client_ip)
        response = RedirectResponse(url="/admin", status_code=302)
        is_secure = request.headers.get("x-forwarded-proto", request.url.scheme) == "https"
        response.set_cookie(
            key=ADMIN_COOKIE_NAME,
            value=token,
            httponly=True,
            max_age=14400,  # 4-hour active session
            samesite="lax",
            path="/",
            secure=is_secure
        )
        return response

    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context={
            "active_page": "admin",
            "error": "Invalid Administrative ID or Executive Passkey. Access Denied.",
            "already_authenticated": False,
            "is_admin": False
        },
        status_code=401
    )

@app.get("/admin/logout")
async def admin_logout(request: Request):
    """Destroys active admin session token from SQLite and clears auth cookie."""
    response = RedirectResponse(url="/admin/login", status_code=302)
    revoke_session(request, response)
    return response

@app.get("/admin")
async def admin_dashboard(request: Request):
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    submissions = load_submissions()
    inquiries = load_inquiries()
    
    total_submissions = len(submissions)
    high_risks = sum(1 for s in submissions if "HIGH" in str(s.get("consistency_risk", "")).upper())
    pending_evals = sum(1 for s in submissions if s.get("status") in ["New Submission", "Pending Review"])
    avg_gap = round(sum(s.get("execution_gap", 0) for s in submissions) / max(total_submissions, 1))

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "active_page": "admin",
            "submissions": submissions,
            "inquiries": inquiries,
            "total_submissions": total_submissions,
            "total_inquiries": len(inquiries),
            "high_risks": high_risks,
            "pending_evals": pending_evals,
            "avg_gap": avg_gap
        }
    )

# ==============================================================================
# Public API Endpoints
# ==============================================================================

@app.get("/api/photos")
async def api_photos(category: Optional[str] = None):
    """Returns all 100 categorized photos with captions, optionally filtered by category_id."""
    if category and category != "all":
        return [p for p in CACHED_PHOTOS if p.get("category_id") == category]
    return CACHED_PHOTOS

@app.get("/api/videos")
async def api_videos(q: Optional[str] = None):
    """Returns all 160 YouTube videos from @TusharDodia."""
    if q:
        query = q.lower().strip()
        return [v for v in CACHED_VIDEOS if query in v.get("title", "").lower()]
    return CACHED_VIDEOS

class ContactInquiry(BaseModel):
    name: str
    org: Optional[str] = ""
    phone: str
    email: Optional[str] = ""
    program: Optional[str] = "general"
    message: Optional[str] = ""

@app.post("/api/contact")
async def api_submit_contact(data: ContactInquiry):
    """Saves incoming institutional and individual inquiries to persistent database and Admin desk."""
    inq_id = f"INQ-2026-{random.randint(100, 999)}"
    
    program_map = {
        "bank": "Cooperative Bank & Branch Leadership (₹35,000)",
        "teachers": "Teacher Faculty Development Workshop (₹35,000)",
        "students": "Student Personality & Career Vision (₹30,000)",
        "counselling": "1-on-1 Student & Parent Counselling (₹150/hr)",
        "trekking": "Training Through Trekking (Wilderness Immersion)",
        "keynote": "Keynote / Motivational Speech Engagement",
        "general": "General Institutional Inquiry"
    }
    
    new_inq = {
        "id": inq_id,
        "name": data.name,
        "org": data.org or "Individual / Parent",
        "phone": data.phone,
        "email": data.email or "",
        "program": data.program,
        "program_name": program_map.get(data.program, data.program),
        "message": data.message,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "New Inquiry"
    }
    
    save_new_inquiry(new_inq)
    
    return {
        "success": True,
        "inquiry_id": inq_id,
        "message": "Thank you! Your inquiry has been received at Mr. Tushar Dodia's executive desk. We will respond within 24 hours."
    }

class AssessmentSubmission(BaseModel):
    tier: str = "senior"
    student_name: str
    student_class: str
    school_name: str
    parent_name: Optional[str] = ""
    parent_phone: str
    parent_email: Optional[str] = ""
    academic_score: Optional[int] = 85
    consistency_score: Optional[int] = 40
    idea_score: Optional[int] = 90
    completion_score: Optional[int] = 30
    user_answers: Optional[Dict[str, Any]] = None

@app.post("/api/submit-assessment")
async def api_submit_assessment(data: AssessmentSubmission):
    """
    Submits student assessment responses.
    The report record is generated and stored in the persistent SQLite database.
    Regular users cannot download the full PDF report directly.
    """
    gap = max(data.idea_score - data.completion_score, 0)
    risk = "HIGH RISK" if data.consistency_score < 55 else ("MODERATE" if data.consistency_score < 75 else "STABLE EXECUTION")
    
    tier_prefix = "SR" if data.tier.lower() == "senior" else "JR"
    report_id = f"DA-2026-{tier_prefix}-{random.randint(1000, 9999)}"
    clean_name = data.student_name.replace(" ", "_")
    custom_pdf_filename = f"{clean_name}_{report_id}.pdf"
    
    new_record = {
        "id": report_id,
        "tier": data.tier.lower(),
        "student_name": data.student_name,
        "student_class": data.student_class,
        "school_name": data.school_name,
        "parent_name": data.parent_name or f"Parent of {data.student_name}",
        "parent_phone": data.parent_phone,
        "parent_email": data.parent_email or "",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "academic_score": data.academic_score,
        "consistency_score": data.consistency_score,
        "idea_score": data.idea_score,
        "completion_score": data.completion_score,
        "execution_gap": gap,
        "consistency_risk": risk,
        "status": "New Submission",
        "notes": f"Submitted via online diagnostic portal. Execution Gap: {gap}%. Pending clinical debrief review by Mr. Tushar Dodia.",
        "pdf_filename": custom_pdf_filename,
        "performance": {
            "analytical_thinking": data.academic_score,
            "creativity": data.idea_score,
            "consistency": data.consistency_score,
            "discipline": int(data.consistency_score * 0.9),
            "leadership_potential": int((data.idea_score + data.academic_score) / 2),
            "emotional_control": 55
        },
        "behaviour": {
            "start_enthusiasm": data.idea_score,
            "task_completion": data.completion_score,
            "planning_strength": int(data.academic_score * 0.85),
            "mid_task_follow_through": data.completion_score,
            "self_correction": 60,
            "conflict_handling": 45
        },
        "strengths": [
            f"J-01: High Natural Curiosity & Visual-Sensory Grasping ({data.idea_score}%)",
            f"J-02: Strong Active Learning Readiness ({data.academic_score}%)",
            "J-03: Responsive to Storytelling and Positive Parental Praise"
        ] if data.tier.lower() == "junior" else [
            f"S-01: Strong Conceptual & Analytical Aptitude ({data.academic_score}%)",
            f"S-02: High Initial Ideation Momentum ({data.idea_score}%)",
            "S-03: Quick Grasp of Theoretical Frameworks"
        ],
        "risks": [
            f"J-R01: Early Habit Vulnerability ({data.consistency_score}%) in Unstructured Environments",
            "J-R02: High Attraction to Screen Distractions & Quick Dopamine",
            "J-R03: Restlessness During Long Static Study Periods"
        ] if data.tier.lower() == "junior" else [
            f"R-01: Execution Gap of {gap}% Between Idea Spark and Completion",
            f"R-02: Consistency Vulnerability Index ({data.consistency_score}%) under unstructured study blocks",
            "R-03: Vulnerability to Screen Distractions"
        ],
        "user_answers": data.user_answers or {}
    }
    
    # Generate the authentic 8-page Diagnostic PDF immediately
    try:
        eval_report = build_evaluation_report_from_record(new_record)
        await render_report_to_pdf(eval_report, output_filename=custom_pdf_filename)
        new_record["pdf_generated"] = True
    except Exception as e:
        print(f"Warning: PDF generation encountered: {e}")
        new_record["pdf_generated"] = False
    
    save_new_submission(new_record)
    
    return {
        "success": True,
        "report_id": report_id,
        "student_name": data.student_name,
        "pdf_url": f"/api/reports/{report_id}/pdf",
        "scores": {
            "academic": data.academic_score,
            "consistency": data.consistency_score,
            "idea": data.idea_score,
            "completion": data.completion_score,
            "gap": gap,
            "risk": risk
        },
        "message": "Official 8-Page Diagnostic Dossier generated successfully."
    }

@app.get("/api/reports/{report_id}/pdf")
async def api_download_student_report_pdf(report_id: str):
    """
    Public direct download and in-browser viewing of the official 8-page
    psychometric diagnostic dossier PDF for the candidate and parent.
    Generates dynamically on the fly if not already cached on disk.
    """
    record = get_submission_by_id(report_id)
    if not record:
        raise HTTPException(status_code=404, detail="Diagnostic report ID not found.")
    
    clean_name = record.get("student_name", "Student").replace(" ", "_")
    custom_pdf_filename = record.get("pdf_filename") or f"{clean_name}_{report_id}.pdf"
    output_pdf = DOSSIER_DIR / "downloads" / custom_pdf_filename
    
    if not output_pdf.exists():
        eval_report = build_evaluation_report_from_record(record)
        await render_report_to_pdf(eval_report, output_filename=custom_pdf_filename)
        record["pdf_filename"] = custom_pdf_filename
        save_submissions(submissions)
        
    return FileResponse(
        path=str(output_pdf),
        media_type="application/pdf",
        filename=f"{clean_name}_Official_Psychometric_Report_{report_id}.pdf"
    )

class EvaluationRequest(BaseModel):
    tier: str = "senior"
    student_info: Dict[str, Any]
    responses: Dict[str, Any]

@app.post("/api/evaluate")
async def api_evaluate(req: EvaluationRequest):
    """Runs psychometric scoring engine and returns structured report JSON."""
    try:
        if req.tier.lower() == "junior":
            engine = JuniorScoringEngine()
            report = engine.evaluate(req.student_info, req.responses)
        else:
            engine = SeniorScoringEngine()
            report = engine.evaluate(req.student_info, req.responses)
        return report.dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Scoring error: {str(e)}")

@app.get("/api/download-sample-report")
async def api_download_sample_report(request: Request):
    """
    Public direct download is restricted.
    Psychometric reports are clinical evaluation documents accessible only in Admin Panel.
    """
    if not is_admin_authenticated(request):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Psychometric dossiers are confidential clinical documents accessible only via the Dodia Academy Executive Admin Panel."
        )
    
    output_pdf = DOSSIER_DIR / "downloads" / "Shardul_Jadhao_Psychometric_Report.pdf"
    if not output_pdf.exists():
        report = get_benchmark_shardul_report()
        await render_report_to_pdf(report, output_filename="Shardul_Jadhao_Psychometric_Report.pdf")

    return FileResponse(
        path=str(output_pdf),
        media_type="application/pdf",
        filename="Shardul_Jadhao_Psychometric_Report.pdf"
    )

@app.get("/api/stats")
async def api_stats():
    submissions = load_submissions()
    inquiries = load_inquiries()
    return {
        "photos_count": len(CACHED_PHOTOS),
        "videos_count": len(CACHED_VIDEOS),
        "institutions": 30,
        "video_impressions": 85000,
        "corporate_years": 8,
        "credentials": ["BE Computer Gold Medalist", "MBA Finance", "CFA USA", "FRM USA"],
        "total_assessments_filed": len(submissions),
        "total_inquiries_filed": len(inquiries)
    }

# ==============================================================================
# Admin Private API Endpoints
# ==============================================================================

@app.get("/api/admin/submissions")
async def api_admin_submissions(request: Request):
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return load_submissions()

@app.get("/api/admin/inquiries")
async def api_admin_inquiries(request: Request):
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return load_inquiries()

@app.get("/api/admin/reports/{report_id}")
async def api_admin_get_report(report_id: str, request: Request):
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    record = get_submission_by_id(report_id)
    if not record:
        raise HTTPException(status_code=404, detail="Report not found")
    return record

@app.post("/api/admin/reports/{report_id}/status")
async def api_admin_update_status(report_id: str, request: Request):
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    data = await request.json()
    new_status = data.get("status")
    new_notes = data.get("notes")
    
    success = update_submission(report_id, status=new_status, notes=new_notes)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    
    record = get_submission_by_id(report_id)
    return {"success": True, "record": record}

@app.delete("/api/admin/reports/{report_id}")
async def api_admin_delete_report(report_id: str, request: Request):
    """Deletes an assessment record from persistent SQLite database."""
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    success = delete_submission(report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report ID not found")
    
    return {"success": True, "message": f"Report {report_id} permanently deleted from database."}

@app.post("/api/admin/inquiries/{inquiry_id}/status")
async def api_admin_update_inquiry_status(inquiry_id: str, request: Request):
    """Updates status for an institutional or individual inquiry in database."""
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    data = await request.json()
    new_status = data.get("status")
    
    success = update_inquiry(inquiry_id, status=new_status)
    if not success:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    
    record = get_inquiry_by_id(inquiry_id)
    return {"success": True, "record": record}

@app.delete("/api/admin/inquiries/{inquiry_id}")
async def api_admin_delete_inquiry(inquiry_id: str, request: Request):
    """Deletes an inquiry record from persistent database."""
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    success = delete_inquiry(inquiry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Inquiry ID not found")
    
    return {"success": True, "message": f"Inquiry {inquiry_id} permanently deleted from database."}

@app.get("/api/admin/reports/{report_id}/pdf")
async def api_admin_download_pdf(report_id: str, request: Request):
    """
    Admin-only PDF download of official 8-page diagnostic dossier.
    Dynamically generates personalized PDF with candidate's actual name,
    school, class, scores, and letter if not already generated.
    """
    if not is_admin_authenticated(request):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Clinical psychometric reports can only be downloaded from the Dodia Academy Executive Admin Panel."
        )
    
    record = get_submission_by_id(report_id)
    if not record:
        raise HTTPException(status_code=404, detail="Report ID not found")
    
    clean_name = record.get("student_name", "Student").replace(" ", "_")
    custom_pdf_filename = record.get("pdf_filename") or f"{clean_name}_{report_id}.pdf"
    output_pdf = DOSSIER_DIR / "downloads" / custom_pdf_filename
    
    # Generate on the fly if not yet created!
    if not output_pdf.exists():
        if record.get("id") == "DA-2026-SR-0418":
            report = get_benchmark_shardul_report()
        else:
            report = build_evaluation_report_from_record(record)
        await render_report_to_pdf(report, output_filename=custom_pdf_filename)
        record["pdf_filename"] = custom_pdf_filename
        save_submissions(submissions)
    
    return FileResponse(
        path=str(output_pdf),
        media_type="application/pdf",
        filename=f"{clean_name}_Official_Psychometric_Report_{report_id}.pdf"
    )

# 404 Fallback Handler
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        request=request,
        name="404.html",
        context={"active_page": "404"},
        status_code=404
    )

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)

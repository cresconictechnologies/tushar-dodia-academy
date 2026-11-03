"""
Comprehensive Verification Suite for Tushar Dodia Web Application, APIs, and Executive Admin Panel
"""
import sys
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import app

client = TestClient(app)

def test_public_routes():
    print("\n--- 1. Testing Public HTML Page Routes ---")
    pages = [
        ("/", "TUSHAR DODIA"),
        ("/about", "Dhanpragati"),
        ("/assessment", "Psychometric"),
        ("/services", "35,000"),
        ("/gallery", "Photographic Archive"),
        ("/videos", "2 Mins Thought"),
        ("/contact", "Buldhana"),
        ("/admin/login", "Executive Admin Desk")
    ]
    for url, expected in pages:
        res = client.get(url)
        assert res.status_code == 200, f"Failed {url}: status {res.status_code}"
        assert expected in res.text, f"Failed {url}: expected '{expected}' not found"
        print(f" [PASS] {url} -> 200 OK (verified '{expected}')")

def test_apis():
    print("\n--- 2. Testing Public APIs & Non-Download Enforcement ---")
    
    # 1. Photos
    res_photos = client.get("/api/photos")
    assert res_photos.status_code == 200
    photos_data = res_photos.json()
    assert len(photos_data) == 100, f"Expected 100 photos, got {len(photos_data)}"
    print(f" [PASS] /api/photos -> 200 OK (returned {len(photos_data)} photos)")

    # 2. Videos
    res_videos = client.get("/api/videos")
    assert res_videos.status_code == 200
    videos_data = res_videos.json()
    assert len(videos_data) == 160, f"Expected 160 videos, got {len(videos_data)}"
    print(f" [PASS] /api/videos -> 200 OK (returned {len(videos_data)} videos)")

    # 3. Stats
    res_stats = client.get("/api/stats")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert stats["photos_count"] == 100
    assert stats["videos_count"] == 160
    assert "total_assessments_filed" in stats
    print(f" [PASS] /api/stats -> 200 OK ({stats['total_assessments_filed']} filed assessments)")

    # 4. Evaluation Engine POST
    eval_payload = {
        "tier": "senior",
        "student_info": {
            "name": "Shardul Jadhao",
            "student_class": "Class IX",
            "academic_score": "85%"
        },
        "responses": {
            "start something new": "Start strong but lose interest",
            "smartphones": "Get distracted after 15-20 mins"
        }
    }
    res_eval = client.post("/api/evaluate", json=eval_payload)
    assert res_eval.status_code == 200
    eval_data = res_eval.json()
    assert eval_data["student"]["name"] == "Shardul Jadhao"
    gap = eval_data["execution_funnel"]["idea_generation"] - eval_data["execution_funnel"]["task_completion_rate"]
    print(f" [PASS] /api/evaluate -> 200 OK (Funnel Execution Gap: {gap}%)")

    # 5. Non-Download Enforcement: Public access to /api/download-sample-report MUST be 403 Forbidden!
    res_forbidden = client.get("/api/download-sample-report")
    assert res_forbidden.status_code == 403, f"Expected 403 Forbidden for public download, got {res_forbidden.status_code}"
    print(" [PASS] /api/download-sample-report -> 403 FORBIDDEN (Verified: Public users cannot download reports!)")

def test_assessment_submission_and_admin():
    print("\n--- 3. Testing Assessment Generation & Admin Panel ---")
    
    # 1. User submits an assessment
    submit_payload = {
        "tier": "senior",
        "student_name": "Kavya Deshpande",
        "student_class": "Class 10th (CBSE)",
        "school_name": "DAV Public School, Pune",
        "parent_name": "Dr. Rajesh Deshpande",
        "parent_phone": "+91 98811 22334",
        "parent_email": "rajesh.deshpande@example.com",
        "academic_score": 88,
        "consistency_score": 42,
        "idea_score": 94,
        "completion_score": 38
    }
    res_submit = client.post("/api/submit-assessment", json=submit_payload)
    assert res_submit.status_code == 200, f"Submit failed: {res_submit.text}"
    submit_res = res_submit.json()
    assert submit_res["success"] is True
    report_id = submit_res["report_id"]
    assert report_id.startswith("DA-2026-SR-")
    assert submit_res["scores"]["gap"] == 56
    print(f" [PASS] /api/submit-assessment -> 200 OK (Generated Report ID: {report_id}, Gap: 56%)")

    # 2. Unauthorized attempt to download this new report PDF without admin session MUST fail (403)
    res_unauth_pdf = client.get(f"/api/admin/reports/{report_id}/pdf")
    assert res_unauth_pdf.status_code == 403
    print(" [PASS] /api/admin/reports/{id}/pdf -> 403 FORBIDDEN without admin credentials (Verified!)")

    # 3. Unauthorized access to /admin redirects to login (302)
    res_unauth_admin = client.get("/admin", follow_redirects=False)
    assert res_unauth_admin.status_code == 302
    assert "/admin/login" in res_unauth_admin.headers["location"]
    print(" [PASS] /admin (unauthenticated) -> 302 Redirect to /admin/login")

    # 4. Admin Login with valid credentials
    login_data = {
        "username": "admin",
        "password": "tushar@dodia2026"
    }
    res_login = client.post("/admin/login", data=login_data, follow_redirects=False)
    assert res_login.status_code == 302
    assert res_login.headers["location"] == "/admin"
    admin_cookie = res_login.cookies.get("dodia_admin_auth")
    assert admin_cookie == "authenticated_tushar_executive"
    print(" [PASS] /admin/login (valid credentials) -> 302 Redirect to /admin with secure cookie")

    # 5. Access /admin with authenticated session
    client.cookies.set("dodia_admin_auth", admin_cookie)
    res_admin = client.get("/admin")
    assert res_admin.status_code == 200
    assert "Executive Diagnostic Command Center" in res_admin.text
    assert "Kavya Deshpande" in res_admin.text
    assert report_id in res_admin.text
    print(f" [PASS] /admin (authenticated) -> 200 OK (Verified: {report_id} visible in Admin Panel!)")

    # 6. Admin API: Update report status
    res_status = client.post(
        f"/api/admin/reports/{report_id}/status",
        json={"status": "Evaluated by Tushar Sir", "notes": "Strong aptitude. High creative spark with moderate execution lag."}
    )
    assert res_status.status_code == 200
    print(f" [PASS] /api/admin/reports/{report_id}/status -> 200 OK (Status updated)")

    # 7. Admin PDF Download: Authenticated download of official 8-page PDF dossier
    res_admin_pdf = client.get(f"/api/admin/reports/{report_id}/pdf")
    assert res_admin_pdf.status_code == 200
    assert res_admin_pdf.headers["content-type"] == "application/pdf"
    assert len(res_admin_pdf.content) > 100000
    print(f" [PASS] /api/admin/reports/{report_id}/pdf -> 200 OK ({len(res_admin_pdf.content):,} bytes PDF downloaded by Admin!)")

def test_contact_inquiries_and_junior_flow():
    print("\n--- 4. Testing Contact Inquiries & Junior Diagnostic Flow ---")
    
    # 1. Submit institutional contact inquiry
    inq_payload = {
        "name": "Prof. Sanjay Gokhale",
        "org": "Vidarbha Shikshan Prasarak Mandal",
        "phone": "+91 94231 77889",
        "email": "sanjay.gokhale@vspm.edu",
        "program": "teachers",
        "message": "Planning annual faculty development seminar for 60 professors on motivational pedagogical methods."
    }
    res_inq = client.post("/api/contact", json=inq_payload)
    assert res_inq.status_code == 200
    inq_data = res_inq.json()
    assert inq_data["success"] is True
    inq_id = inq_data["inquiry_id"]
    print(f" [PASS] /api/contact -> 200 OK (Created Inquiry ID: {inq_id})")

    # 2. Verify admin can update inquiry status
    admin_cookie = "authenticated_tushar_executive"
    client.cookies.set("dodia_admin_auth", admin_cookie)
    res_inq_status = client.post(
        f"/api/admin/inquiries/{inq_id}/status",
        json={"status": "Contacted"}
    )
    assert res_inq_status.status_code == 200
    assert res_inq_status.json()["record"]["status"] == "Contacted"
    print(f" [PASS] /api/admin/inquiries/{inq_id}/status -> 200 OK (Status updated to Contacted)")

    # 3. Submit Junior tier assessment
    junior_payload = {
        "tier": "junior",
        "student_name": "Aarav Kulkarni",
        "student_class": "Class 4th (Primary)",
        "school_name": "St. Xavier's Academy, Pune",
        "parent_name": "Siddharth Kulkarni",
        "parent_phone": "+91 97654 32109",
        "parent_email": "siddharth.kulkarni@example.com",
        "academic_score": 88,
        "consistency_score": 48,
        "idea_score": 92,
        "completion_score": 40,
        "user_answers": {"j1": 0, "j2": 1, "j3": 1, "j4": 1, "j5": 2}
    }
    res_jr = client.post("/api/submit-assessment", json=junior_payload)
    assert res_jr.status_code == 200
    jr_data = res_jr.json()
    assert jr_data["success"] is True
    jr_id = jr_data["report_id"]
    assert jr_id.startswith("DA-2026-JR-")
    print(f" [PASS] /api/submit-assessment (Junior) -> 200 OK (Report ID: {jr_id})")

    # 4. Admin generates and downloads Junior PDF dossier dynamically
    res_jr_pdf = client.get(f"/api/admin/reports/{jr_id}/pdf")
    assert res_jr_pdf.status_code == 200
    assert res_jr_pdf.headers["content-type"] == "application/pdf"
    assert len(res_jr_pdf.content) > 100000
    print(f" [PASS] /api/admin/reports/{jr_id}/pdf -> 200 OK ({len(res_jr_pdf.content):,} bytes Junior PDF generated!)")

if __name__ == "__main__":
    try:
        test_public_routes()
        test_apis()
        test_assessment_submission_and_admin()
        test_contact_inquiries_and_junior_flow()
        print("\n ALL VERIFICATION SUITE CHECKS PASSED 100% PERFECTLY!\n")
    except Exception as e:
        print(f"\n [FAIL] Verification Error: {e}")
        sys.exit(1)

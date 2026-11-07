"""
Comprehensive E2E Verification Suite for Tushar Dodia & Dodia Academy Platform.
Tests all pages, APIs, forms, scoring engines, restricted security, admin authentication,
and dynamic 8-page PDF generation across local and live Render environments.
"""
import sys
import time
import requests

def run_suite(base_url: str):
    print(f"\n{'='*75}")
    print(f"RUNNING E2E VERIFICATION SUITE AGAINST: {base_url}")
    print(f"{'='*75}\n")
    
    passed = 0
    failed = 0
    
    def test_assert(desc: str, condition: bool, extra: str = ""):
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  [PASS] {desc}")
        else:
            failed += 1
            print(f"  [FAIL] {desc} - {extra}")

    # -------------------------------------------------------------
    # 0. DEDICATED HEALTH CHECK & OWASP SECURITY HEADERS
    # -------------------------------------------------------------
    print("\n--- 0. Testing Dedicated Health Check & OWASP Security Headers ---")
    health_res = requests.get(f"{base_url}/api/health", timeout=20)
    test_assert("GET /api/health returns 200", health_res.status_code == 200)
    health_json = health_res.json()
    test_assert("Health payload has 'status': 'healthy'", health_json.get("status") == "healthy")
    test_assert("Health payload reports repository status", "repository" in health_json or "database" in health_json)
    
    # Verify OWASP Security Headers
    test_assert("X-Content-Type-Options: nosniff present", health_res.headers.get("X-Content-Type-Options") == "nosniff")
    test_assert("X-Frame-Options: SAMEORIGIN present", health_res.headers.get("X-Frame-Options") == "SAMEORIGIN")
    test_assert("Content-Security-Policy header present", "Content-Security-Policy" in health_res.headers)
    test_assert("Referrer-Policy header present", "Referrer-Policy" in health_res.headers)

    # -------------------------------------------------------------
    # 1. PUBLIC WEB PAGES
    # -------------------------------------------------------------
    print("--- 1. Testing Public Web Pages ---")
    pages = [
        ("/", "Modern Strategy", "Home Page"),
        ("/about", "Mr. Tushar Jagdish Dodia", "About Page"),
        ("/services", "Programs Engineered for Real Institutional Impact", "Services Page"),
        ("/gallery", "Visual Evidence of Transformation", "Gallery Page"),
        ("/videos", "Video Wisdom Vault", "Videos Page"),
        ("/contact", "Initiate an Institutional Dialogue", "Contact Page"),
        ("/assessment", "Psychometric Assessment", "Assessment Page"),
        ("/admin/login", "Executive Admin Desk", "Admin Login Page")
    ]
    for path, keyword, label in pages:
        res = requests.get(f"{base_url}{path}", timeout=20)
        test_assert(f"{label} (GET {path}) returns 200", res.status_code == 200, f"Got {res.status_code}")
        test_assert(f"{label} contains '{keyword}'", keyword in res.text, f"Keyword '{keyword}' missing")

    # -------------------------------------------------------------
    # 2. ANCIENT WISDOM HIGHLIGHTS
    # -------------------------------------------------------------
    print("\n--- 2. Testing Ancient Wisdom Content & References ---")
    home_res = requests.get(f"{base_url}/", timeout=20)
    test_assert("Lord Ram Maryada paradigm present", "Lord Ram: The Maryada" in home_res.text)
    test_assert("Lord Krishna dynamic realpolitik present", "Lord Krishna: Dynamic Realpolitik" in home_res.text)
    test_assert("Chhatrapati Shivaji Maharaj mawala empowerment present", "Chhatrapati Shivaji Maharaj: Grounded Grit" in home_res.text)
    test_assert("Sahyadri Trekking documented reference cited", "Slide 18" in home_res.text)

    # -------------------------------------------------------------
    # 3. RESTRICTED DOWNLOAD ACCESS (SECURITY RULE)
    # -------------------------------------------------------------
    print("\n--- 3. Testing Restricted Download Security ---")
    sample_res = requests.get(f"{base_url}/api/download-sample-report", timeout=20)
    test_assert("Public PDF download is BLOCKED (403 Forbidden)", sample_res.status_code == 403, f"Got {sample_res.status_code}")

    # Unauthenticated admin access should redirect (302)
    admin_unauth = requests.get(f"{base_url}/admin", timeout=20, allow_redirects=False)
    test_assert("Unauthenticated /admin redirects to login (302)", admin_unauth.status_code == 302, f"Got {admin_unauth.status_code}")

    # -------------------------------------------------------------
    # 4. DATA APIS
    # -------------------------------------------------------------
    print("\n--- 4. Testing Public Data APIs ---")
    photos_res = requests.get(f"{base_url}/api/photos", timeout=20)
    test_assert("GET /api/photos returns 200", photos_res.status_code == 200)
    photos = photos_res.json()
    test_assert("Photos array has >= 50 images", len(photos) >= 50, f"Count: {len(photos)}")

    videos_res = requests.get(f"{base_url}/api/videos", timeout=20)
    test_assert("GET /api/videos returns 200", videos_res.status_code == 200)
    videos = videos_res.json()
    test_assert("Videos array has >= 10 lectures", len(videos) >= 10, f"Count: {len(videos)}")

    # -------------------------------------------------------------
    # 5. CONTACT FORM SUBMISSION
    # -------------------------------------------------------------
    print("\n--- 5. Testing Contact Form Submission ---")
    contact_data = {
        "name": "Dr. Virendra Kulkarni",
        "email": "virendra.kulkarni@symbiosis.ac.in",
        "phone": "+91 98220 12345",
        "org": "Symbiosis Institute of Business Management",
        "program": "Corporate Leadership & High-Performance Culture",
        "message": "We would like to invite Mr. Tushar Dodia for a 2-day faculty and executive training program."
    }
    contact_res = requests.post(f"{base_url}/api/contact", json=contact_data, timeout=20)
    test_assert("POST /api/contact returns 200", contact_res.status_code == 200, f"Got {contact_res.status_code}")
    c_json = contact_res.json()
    test_assert("Contact response success is True", c_json.get("success") is True)
    test_inquiry_id = c_json.get("inquiry_id")
    test_assert("Contact returns valid Inquiry ID (INQ-2026-...)", bool(test_inquiry_id and test_inquiry_id.startswith("INQ-2026-")))

    # -------------------------------------------------------------
    # 6. PSYCHOMETRIC ASSESSMENT SUBMISSION (SENIOR & JUNIOR)
    # -------------------------------------------------------------
    print("\n--- 6. Testing Psychometric Diagnostic Engines ---")
    
    # Senior Assessment
    sr_payload = {
        "tier": "senior",
        "student_name": "Siddharth Verma",
        "student_class": "11th Science",
        "school_name": "Bishop's High School Pune",
        "parent_name": "Anil Verma",
        "parent_email": "anil.verma@example.com",
        "parent_phone": "+91 98900 11223",
        "academic_score": 86,
        "consistency_score": 42,
        "idea_score": 92,
        "completion_score": 34,
        "user_answers": {str(i): (3 if i % 2 == 0 else 5) for i in range(1, 31)}
    }
    sr_res = requests.post(f"{base_url}/api/submit-assessment", json=sr_payload, timeout=20)
    test_assert("POST /api/submit-assessment (Senior) returns 200", sr_res.status_code == 200, f"Got {sr_res.status_code}")
    sr_json = sr_res.json()
    test_assert("Senior submission success is True", sr_json.get("success") is True)
    sr_report_id = sr_json.get("report_id")
    test_assert("Senior Report ID generated (DA-2026-SR-...)", bool(sr_report_id and sr_report_id.startswith("DA-2026-SR-")), f"Got {sr_report_id}")
    test_assert("Senior scores contains execution gap", "gap" in sr_json.get("scores", {}))
    test_assert("Senior scores contains risk tier", "risk" in sr_json.get("scores", {}))
    test_assert("Senior submission returns pdf_url", "pdf_url" in sr_json)
    
    # Test Public Report Download
    public_pdf_res = requests.get(f"{base_url}{sr_json['pdf_url']}", timeout=60)
    test_assert("Public report PDF download returns 200", public_pdf_res.status_code == 200)
    test_assert("Public report starts with %PDF", public_pdf_res.content[:4] == b"%PDF")
    test_assert("Public report size > 500KB", len(public_pdf_res.content) > 500000)

    # Junior Assessment
    jr_payload = {
        "tier": "junior",
        "student_name": "Rhea Kulkarni",
        "student_class": "Class 4th",
        "school_name": "Vibgyor High School",
        "parent_name": "Pooja Kulkarni",
        "parent_email": "pooja.k@example.com",
        "parent_phone": "+91 98230 44556",
        "academic_score": 88,
        "consistency_score": 48,
        "idea_score": 90,
        "completion_score": 42,
        "user_answers": {str(i): (1 if i % 2 == 0 else 0) for i in range(1, 31)}
    }
    jr_res = requests.post(f"{base_url}/api/submit-assessment", json=jr_payload, timeout=20)
    test_assert("POST /api/submit-assessment (Junior) returns 200", jr_res.status_code == 200, f"Got {jr_res.status_code}")
    jr_json = jr_res.json()
    test_assert("Junior submission success is True", jr_json.get("success") is True)
    jr_report_id = jr_json.get("report_id")
    test_assert("Junior Report ID generated (DA-2026-JR-...)", bool(jr_report_id and jr_report_id.startswith("DA-2026-JR-")), f"Got {jr_report_id}")

    # -------------------------------------------------------------
    # 7. ADMIN AUTHENTICATION & MANAGEMENT
    # -------------------------------------------------------------
    print("\n--- 7. Testing Admin Authentication & Dashboard ---")
    session = requests.Session()
    
    # Bad Login
    bad_login = session.post(f"{base_url}/admin/login", data={"username": "wrong", "password": "wrongpassword"}, timeout=20)
    test_assert("Bad admin login fails (rejected with error message)", "Invalid username or password" in bad_login.text or bad_login.status_code == 401)

    # Valid Login
    login_res = session.post(f"{base_url}/admin/login", data={"username": "admin", "password": "tushar@dodia2026"}, timeout=20, allow_redirects=False)
    test_assert("Valid admin login redirects (302)", login_res.status_code == 302, f"Got {login_res.status_code}")
    test_assert("Admin auth cookie established", "dodia_admin_auth" in session.cookies.get_dict())

    # Dashboard Access
    admin_dash = session.get(f"{base_url}/admin", timeout=20)
    test_assert("Authenticated /admin returns 200", admin_dash.status_code == 200)
    test_assert("Admin dashboard shows submissions section", "Confidential Student Diagnostic Records" in admin_dash.text)
    test_assert("Newly submitted senior report present in dashboard", sr_report_id in admin_dash.text)

    # Admin API: Status Update for Report
    status_update_res = session.post(f"{base_url}/api/admin/reports/{sr_report_id}/status", json={"status": "Evaluated by Tushar Sir"}, timeout=20)
    test_assert("POST update report status returns 200", status_update_res.status_code == 200)
    test_assert("Report status successfully updated", status_update_res.json().get("record", {}).get("status") == "Evaluated by Tushar Sir")

    # Admin API: Status Update for Inquiry
    inq_update_res = session.post(f"{base_url}/api/admin/inquiries/{test_inquiry_id}/status", json={"status": "Contacted"}, timeout=20)
    test_assert("POST update inquiry status returns 200", inq_update_res.status_code == 200)
    test_assert("Inquiry status successfully updated", inq_update_res.json().get("record", {}).get("status") == "Contacted")

    # Admin API: Get Report Details
    detail_res = session.get(f"{base_url}/api/admin/reports/{sr_report_id}", timeout=20)
    test_assert("GET single report details returns 200", detail_res.status_code == 200)
    test_assert("Report details has performance scores", "performance" in detail_res.json())

    # -------------------------------------------------------------
    # 8. HEADLESS PLAYWRIGHT 8-PAGE PDF GENERATION
    # -------------------------------------------------------------
    print("\n--- 8. Testing On-Demand 8-Page PDF Generation ---")
    print(f"Requesting dynamic PDF for report {sr_report_id} (this triggers headless Chromium)...")
    pdf_start = time.time()
    pdf_res = session.get(f"{base_url}/api/admin/reports/{sr_report_id}/pdf", timeout=75)
    pdf_duration = time.time() - pdf_start
    test_assert(f"GET /api/admin/reports/{sr_report_id}/pdf returns 200 (took {pdf_duration:.1f}s)", pdf_res.status_code == 200, f"Got {pdf_res.status_code}")
    test_assert("PDF content-type is application/pdf", pdf_res.headers.get("content-type") == "application/pdf")
    test_assert("PDF binary starts with '%PDF'", pdf_res.content[:4] == b"%PDF")
    test_assert("PDF file size is > 500 KB", len(pdf_res.content) > 500000, f"Size: {len(pdf_res.content)} bytes")

    # -------------------------------------------------------------
    # 9. ADMIN LOGOUT
    # -------------------------------------------------------------
    print("\n--- 9. Testing Admin Logout ---")
    logout_res = session.get(f"{base_url}/admin/logout", timeout=20, allow_redirects=False)
    test_assert("GET /admin/logout redirects (302)", logout_res.status_code == 302)

    # SUMMARY
    print(f"\n{'='*75}")
    print(f"E2E SUITE RESULTS: {passed} PASSED | {failed} FAILED")
    print(f"{'='*75}\n")
    return failed == 0

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    success = run_suite(target)
    sys.exit(0 if success else 1)

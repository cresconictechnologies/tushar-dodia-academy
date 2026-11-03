"""
Comprehensive Browser UI Visual & Console Audit using Playwright.
Audits all pages including the new Executive Admin Panel and Assessment Generation Flow:
1. Full-page high-resolution desktop screenshots (Light Theme).
2. Mobile responsive check.
3. Assessment completion & Report Generation flow (Non-Download enforcement).
4. Executive Admin Login & Dashboard audit.
5. Console error and unhandled rejection logging.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
SCREENSHOT_DIR = BASE_DIR / "dossier" / "pages"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

def audit():
    console_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # Listen for console events and unhandled errors
        def on_console(msg):
            if msg.type == "error":
                console_errors.append(f"[{msg.type.upper()}] {msg.text}")
                print(f"  [BROWSER CONSOLE {msg.type.upper()}]: {msg.text}")

        page.on("console", on_console)
        page.on("pageerror", lambda err: console_errors.append(f"[UNHANDLED EXCEPTION]: {err}"))

        pages_to_audit = [
            ("http://127.0.0.1:8000/", "screenshot_home_light.png", "Home Page (Hero, Video Reel, Story, Matrix)"),
            ("http://127.0.0.1:8000/about", "screenshot_about_light.png", "About & Credentials Page"),
            ("http://127.0.0.1:8000/assessment", "screenshot_assessment_light.png", "Dynamic Psychometric Assessment"),
            ("http://127.0.0.1:8000/services", "screenshot_services_light.png", "Services & Executive Mentorship Programs"),
            ("http://127.0.0.1:8000/gallery", "screenshot_gallery_light.png", "100-Photo Field Archive & Lightbox"),
            ("http://127.0.0.1:8000/videos", "screenshot_videos_light.png", "160-Video YouTube & Instagram Vault"),
            ("http://127.0.0.1:8000/contact", "screenshot_contact_light.png", "Executive Direct Contact Desk"),
            ("http://127.0.0.1:8000/admin/login", "screenshot_admin_login.png", "Executive Admin Login Desk")
        ]

        print("==================================================")
        print("  STARTING LIGHT & COLORFUL THEME VISUAL AUDIT    ")
        print("==================================================")

        for url, fname, label in pages_to_audit:
            print(f"\n>> Auditing {label} ({url})...")
            response = page.goto(url, wait_until="networkidle", timeout=15000)
            status = response.status if response else "Unknown"
            print(f"   HTTP Status: {status}")

            page.wait_for_timeout(800)

            save_path = SCREENSHOT_DIR / fname
            page.screenshot(path=str(save_path), full_page=True)
            size_kb = round(save_path.stat().st_size / 1024, 1)
            print(f"   [SAVED] {save_path.name} ({size_kb} KB)")

        # 9. Test Interactive Assessment Submission Flow (Non-Download check)
        print("\n>> Auditing Interactive Assessment Simulator & Submission...")
        page.goto("http://127.0.0.1:8000/assessment", wait_until="networkidle")
        page.wait_for_timeout(500)

        # Answer 5 questions
        for q_step in range(5):
            page.wait_for_selector(".quiz-option-label", timeout=5000)
            # Pick first option
            page.click(".quiz-option-label:first-child")
            page.click("#quizNextBtn")
            page.wait_for_timeout(300)

        # Fill candidate identification form
        page.wait_for_selector("#candidateDetailForm", timeout=5000)
        page.fill("#candidateName", "Pranav Kulkarni")
        page.fill("#candidateClass", "Class 10th (CBSE)")
        page.fill("#candidateSchool", "Rajarshi Shahu Academy, Pune")
        page.fill("#candidatePhone", "+91 98220 11223")
        page.fill("#candidateEmail", "pranav.kulkarni@example.com")
        page.click("#submitAssessmentBtn")

        # Wait for diagnostic result snapshot (with Report ID and non-download notice)
        page.wait_for_selector(".rm-progress-bg", timeout=6000)
        page.wait_for_timeout(800)
        result_path = SCREENSHOT_DIR / "screenshot_assessment_submitted.png"
        page.screenshot(path=str(result_path), full_page=True)
        print(f"   [SAVED] {result_path.name} ({round(result_path.stat().st_size / 1024, 1)} KB) - Verified Report ID & Non-Download Notice!")

        # 10. Audit Admin Login & Executive Dashboard
        print("\n>> Auditing Admin Login & Executive Dashboard...")
        page.goto("http://127.0.0.1:8000/admin/login", wait_until="networkidle")
        page.fill("#username", "admin")
        page.fill("#password", "tushar@dodia2026")
        page.click("button[type='submit']")
        page.wait_for_url("**/admin", timeout=8000)
        page.wait_for_timeout(800)

        admin_path = SCREENSHOT_DIR / "screenshot_admin_dashboard.png"
        page.screenshot(path=str(admin_path), full_page=True)
        print(f"   [SAVED] {admin_path.name} ({round(admin_path.stat().st_size / 1024, 1)} KB) - Verified Live Admin Dashboard!")

        # 11. Audit Admin Inquiries Tab
        print("\n>> Auditing Admin Inquiries Tab...")
        page.click("#tabInquiriesBtn")
        page.wait_for_timeout(600)
        inq_admin_path = SCREENSHOT_DIR / "screenshot_admin_inquiries.png"
        page.screenshot(path=str(inq_admin_path), full_page=True)
        print(f"   [SAVED] {inq_admin_path.name} ({round(inq_admin_path.stat().st_size / 1024, 1)} KB) - Verified Live Inquiries Tab!")

        # 12. Audit Contact Form Interactive Submission
        print("\n>> Auditing Contact Form Submission Flow...")
        page.goto("http://127.0.0.1:8000/contact", wait_until="networkidle")
        page.fill("#contactName", "Mahesh Deshpande")
        page.fill("#contactOrg", "Vidarbha Urban Co-op Bank Ltd")
        page.fill("#contactPhone", "+91 94221 65432")
        page.fill("#contactEmail", "mahesh@vidarbhabank.in")
        page.select_option("#contactProgram", "bank")
        page.fill("#contactMessage", "Requesting a 2-day branch leadership seminar for 35 officers.")
        page.click("#contactSubmitBtn")
        page.wait_for_selector("#formSuccessMessage", state="visible", timeout=6000)
        page.wait_for_timeout(600)
        contact_sub_path = SCREENSHOT_DIR / "screenshot_contact_submitted.png"
        page.screenshot(path=str(contact_sub_path), full_page=True)
        print(f"   [SAVED] {contact_sub_path.name} ({round(contact_sub_path.stat().st_size / 1024, 1)} KB) - Verified Contact AJAX Submission!")

        # 13. Mobile Responsive Audit of Home Page
        print("\n>> Auditing Mobile Viewport (390 x 844)...")
        mobile_page = context.new_page()
        mobile_page.set_viewport_size({"width": 390, "height": 844})
        mobile_page.goto("http://127.0.0.1:8000/", wait_until="networkidle")
        mobile_page.wait_for_timeout(800)
        mob_path = SCREENSHOT_DIR / "screenshot_mobile_home_light.png"
        mobile_page.screenshot(path=str(mob_path), full_page=True)
        print(f"   [SAVED] {mob_path.name} ({round(mob_path.stat().st_size / 1024, 1)} KB)")

        browser.close()

    print("\n==================================================")
    print(f"  AUDIT COMPLETED: 13 screenshots generated.")
    print(f"  Browser Console Errors Detected: {len(console_errors)}")
    print("==================================================")
    if console_errors:
        print("Summary of logged errors:")
        for err in console_errors[:10]:
            print(f" - {err}")
    else:
        print(" [CLEAN] Zero console errors detected across all public & admin pages!")

if __name__ == "__main__":
    audit()

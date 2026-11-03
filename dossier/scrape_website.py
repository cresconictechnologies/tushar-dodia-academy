import os
import re
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

PAGES = [
    {
        "name": "home",
        "url": "https://www.consultwithtushardodia.com"
    },
    {
        "name": "cooperative_bank_training",
        "url": "https://www.consultwithtushardodia.com/service-page/cooperative-bank-training-solutions"
    },
    {
        "name": "student_personality_development",
        "url": "https://www.consultwithtushardodia.com/service-page/student-personality-development"
    },
    {
        "name": "teacher_training_and_development",
        "url": "https://www.consultwithtushardodia.com/service-page/teacher-training-and-development"
    },
    {
        "name": "booking_calendar",
        "url": "https://www.consultwithtushardodia.com/booking-calendar"
    }
]

BASE_DIR = r"c:\projects\tushar sir dodia\dossier"
PAGES_DIR = os.path.join(BASE_DIR, "pages")
ASSETS_DIR = os.path.join(BASE_DIR, "web_assets")

os.makedirs(PAGES_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

all_image_urls = set()
scraped_data = {}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    for item in PAGES:
        name = item["name"]
        url = item["url"]
        print(f"Scraping {name}: {url}...")
        try:
            response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(4)  # Let Wix hydration / dynamic elements settle

            # Scroll to trigger lazy loading of images
            page.evaluate("""async () => {
                await new Promise((resolve) => {
                    let totalHeight = 0;
                    let distance = 300;
                    let timer = setInterval(() => {
                        let scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;
                        if(totalHeight >= scrollHeight){
                            clearInterval(timer);
                            resolve();
                        }
                    }, 100);
                });
            }""")
            time.sleep(2)

            html_content = page.content()
            title = page.title()

            # Save full HTML
            html_file = os.path.join(PAGES_DIR, f"{name}.html")
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Parse with BeautifulSoup to extract clean text
            soup = BeautifulSoup(html_content, "html.parser")
            # Remove scripts and styles
            for s in soup(["script", "style", "noscript"]):
                s.extract()

            text_content = soup.get_text(separator="\n", strip=True)
            txt_file = os.path.join(PAGES_DIR, f"{name}.txt")
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write(f"Title: {title}\nURL: {url}\n\n{text_content}")

            # Collect image URLs
            # 1. <img> tags src and srcset
            for img in soup.find_all("img"):
                src = img.get("src")
                if src:
                    all_image_urls.add(urllib.parse.urljoin(url, src))
                srcset = img.get("srcset")
                if srcset:
                    for part in srcset.split(","):
                        u = part.strip().split(" ")[0]
                        if u:
                            all_image_urls.add(urllib.parse.urljoin(url, u))

            # 2. background images in inline style
            for el in soup.find_all(style=True):
                style = el["style"]
                matches = re.findall(r'url\([\'"]?(.*?)[\'"]?\)', style)
                for m in matches:
                    if m and not m.startswith("data:"):
                        all_image_urls.add(urllib.parse.urljoin(url, m))

            # 3. Wix specific image patterns in html
            # Wix often uses static.wixstatic.com/media/...
            wix_matches = re.findall(r'https://static\.wixstatic\.com/media/[a-zA-Z0-9_\.~%-]+', html_content)
            for wm in wix_matches:
                # clean up any trailing quotes or params
                wm_clean = wm.split("?")[0].split('"')[0].split("'")[0]
                all_image_urls.add(wm_clean)

            # Take screenshot of each page for proof / visual reference
            screenshot_file = os.path.join(PAGES_DIR, f"{name}.png")
            page.screenshot(path=screenshot_file, full_page=True)
            print(f"Captured {name}: {len(text_content)} chars text, screenshot saved.")

            scraped_data[name] = {
                "title": title,
                "url": url,
                "text_length": len(text_content)
            }
        except Exception as e:
            print(f"Error scraping {name} ({url}): {e}")

    browser.close()

print(f"\nFound {len(all_image_urls)} unique image candidate URLs.")

# Download all images
downloaded_images = []
for idx, img_url in enumerate(sorted(all_image_urls)):
    if not img_url.startswith("http"):
        continue
    # Filter out common junk svgs or small icons if desired, but let's download everything useful
    parsed = urllib.parse.urlparse(img_url)
    filename = os.path.basename(parsed.path)
    if not filename or len(filename) > 80:
        ext = ".jpg"
        if ".png" in img_url.lower():
            ext = ".png"
        elif ".webp" in img_url.lower():
            ext = ".webp"
        elif ".svg" in img_url.lower():
            ext = ".svg"
        filename = f"image_{idx+1}{ext}"

    # clean filename of special chars
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    if not any(filename.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".svg", ".gif", ".ico"]):
        filename = f"{filename}_{idx+1}.jpg"

    dest = os.path.join(ASSETS_DIR, f"{idx+1:03d}_{filename}")
    try:
        r = requests.get(img_url, headers=headers, timeout=20)
        if r.status_code == 200 and len(r.content) > 100:  # avoid 0-byte or trivial stub
            with open(dest, "wb") as f:
                f.write(r.content)
            downloaded_images.append({
                "url": img_url,
                "file": dest,
                "size": len(r.content)
            })
            print(f"[{idx+1}/{len(all_image_urls)}] Downloaded {filename} ({len(r.content)} bytes)")
    except Exception as e:
        print(f"Failed to download {img_url}: {e}")

print(f"\nSuccessfully downloaded {len(downloaded_images)} images into {ASSETS_DIR}")

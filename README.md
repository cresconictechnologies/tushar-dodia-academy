# Tushar Dodia & Dodia Academy — Official Web Portal & Psychometric Diagnostic Platform

> **"Modern Strategy. Ancient Wisdom."**  
> Bridging corporate governance, CFA/FRM quantitative risk analysis, and institutional excellence with classical Indian philosophical principles.

---

## 🌟 Executive Summary & Scope

This repository contains the complete reverse-engineered psychometric evaluation engine, digital research dossier, and production-grade dynamic web application for **Mr. Tushar Dodia** (BE Computer Gold Medalist, MBA Finance, CFA USA, FRM USA, Founding Director of Dhanpragati Urban Nidhi Ltd).

### 🚀 Key Components Delivered

1. **Psychometric Evaluation Engine & Schemas (`engine/`):**
   - **Junior Assessment (Ages 4–11):** 8 Sections, 79 Questions (`junior_schema.json`) evaluating sensory modalities (VARK), attention span, frustration tolerance, and parent routine structure.
   - **Senior Assessment (Ages 12–16):** 9 Sections, 75 Questions (`senior_schema.json`) diagnosing academic grit, consistency risk, execution funnel attrition, and career alignment.
   - **8-Page Branded PDF Generator (`generator/`):** Reproduces the exact pixel-perfect diagnostic report issued for students like *Shardul Jadhao*, with Devanagari typography, execution funnel diagrams, strengths (S-01 to S-07), risk radars (R-01 to R-06), and Tushar Sir's personal letter to parents.

2. **Digital Intelligence Dossier (`dossier/`):**
   - **100 Categorized Photographic Slides (`dossier/photos/`):** Segregated into 8 semantic directories with full bilingual Marathi/Hindi/English captions in `PHOTO_INDEX.csv` and `PHOTO_CATALOG.md`.
   - **160 YouTube Video Vault (`dossier/youtube_videos.json`):** Full metadata for all videos on `@TusharDodia` (85,000+ views, "2 Mins Thought" series).
   - **Institutional Data:** MCA Director details (DIN: 10265315, CIN: U64990MH2023PLN407987), client track record (Rajarshi Shahu Bank, Buldhana Urban, LPU Punjab), and official pricing (₹35k Bank, ₹35k Teacher, ₹30k Student, ₹150/hr Counselling).

3. **Production Dynamic Multipage Web Portal (`web/` & `app.py`):**
   - **Dynamic Framework:** FastAPI + Jinja2 + GSAP ScrollTrigger + Custom Responsive CSS.
   - **Pages:**
     - `/` (Grand Landing Page with animated counters, Tri-Pillar Model, marquee, and live quiz simulator)
     - `/about` (Biography, corporate Wall Street track, MCA directorship, and career timeline)
     - `/assessment` (Psychometric hub with direct Google Form links, live interactive 5-question simulator, and 1-click 8-page PDF download)
     - `/services` (Institutional banking, teacher development, student bootcamps, and wilderness treks with pricing)
     - `/gallery` (100-slide categorized photo archive with fullscreen lightbox and bilingual captions)
     - `/videos` (160-video wisdom vault with instant client-side search and inline modal video player)
     - `/contact` (Inquiry form, Buldhana headquarters coordinates, direct WhatsApp, and phone)
   - **Verified API Endpoints:**
     - `GET /api/photos`
     - `GET /api/videos`
     - `POST /api/evaluate`
     - `GET /api/download-sample-report`
     - `GET /api/stats`

---

## 🛠️ Quickstart & Server Launch

The server runs on **Python 3.14+** using FastAPI and Uvicorn:

```bash
# Start server locally on port 8000
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Visit in your browser:
- **Homepage:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Psychometric Hub:** [http://127.0.0.1:8000/assessment](http://127.0.0.1:8000/assessment)
- **100-Photo Archive:** [http://127.0.0.1:8000/gallery](http://127.0.0.1:8000/gallery)
- **160-Video Vault:** [http://127.0.0.1:8000/videos](http://127.0.0.1:8000/videos)
- **Institutional Services:** [http://127.0.0.1:8000/services](http://127.0.0.1:8000/services)
- **API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Automated Verification

Run the automated test suite to verify all HTML routes, API data integrity, and PDF generation:

```bash
python verify_web.py
```

---

## 🏢 Corporate & Statutory Details
- **Founder & Assessor:** Mr. Tushar Jagdish Dodia
- **Director Identification Number (DIN):** `10265315`
- **Institution:** Dhanpragati Urban Nidhi Limited (CIN: `U64990MH2023PLN407987`)
- **Academy:** Dodia Academy of Education & Human Development
- **Headquarters:** Buldhana, Maharashtra 443001, India
- **Direct WhatsApp:** `+91 7741823212`

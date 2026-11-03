"""
PDF Generation Service using Jinja2 and Playwright Headless Chromium.
Renders pixel-perfect 8-page branded Psychometric Test Reports for any candidate.
"""
import os
import sys
import asyncio
import base64
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from jinja2 import Environment, FileSystemLoader
from engine.scorer_senior import SeniorScoringEngine
from engine.scorer_junior import JuniorScoringEngine
from engine.common import (
    EvaluationReport, StudentProfile, PerformanceSnapshot, BehaviourSnapshot,
    ExecutionFunnel, StrengthItem, RiskItem
)

TEMPLATES_DIR = BASE_DIR / "generator" / "templates"
OUTPUT_DIR = BASE_DIR / "dossier" / "downloads"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LOGO_PATH = BASE_DIR / "web" / "static" / "img" / "logo.png"

env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

def get_logo_base64() -> str:
    """Returns base64 encoded string of the official Dodia Academy emblem."""
    if LOGO_PATH.exists():
        try:
            with open(LOGO_PATH, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return ""
    return ""

def get_benchmark_shardul_report() -> EvaluationReport:
    """Returns the calibrated benchmark report for Shardul Jadhao."""
    engine = SeniorScoringEngine()
    student_info = {
        "name": "Shardul Jadhao",
        "student_class": "Class IX",
        "academic_score": "85%",
        "father_occupation": "Senior Government Official / Agri-Business Leader",
        "mother_occupation": "Homemaker & Family Foundation Director",
        "assessment_date": "March 2026",
        "report_id": "DA-2026-SR-0418"
    }
    responses = {
        "start something new": "Start strong but lose interest",
        "smartphones": "Get distracted after 15-20 mins",
        "pressure": "Perform under pressure",
        "feedback": "Feel defensive initially"
    }
    return engine.evaluate(student_info, responses)

def build_evaluation_report_from_record(record: Dict[str, Any]) -> EvaluationReport:
    """
    Constructs a customized, authentic 8-page EvaluationReport object from any
    assessment submission record stored in the Admin Repository.
    """
    tier = record.get("tier", "senior").lower()
    student_name = record.get("student_name", "Student")
    student_class = record.get("student_class", "Class IX")
    academic_pct = record.get("academic_score", 85)
    report_id = record.get("id", "DA-2026-SR-0001")
    parent_name = record.get("parent_name", "Guardian")
    created_at = record.get("created_at", "May 2026")[:10]
    
    student_info = {
        "name": student_name,
        "student_class": student_class,
        "academic_score": f"{academic_pct}%",
        "father_name": parent_name,
        "father_occupation": f"Guardian / Family ({record.get('school_name', '')})",
        "mother_name": "Family Support",
        "mother_occupation": "Homemaker",
        "assessment_date": created_at,
        "report_id": report_id
    }
    
    responses = record.get("user_answers", {})
    if tier == "junior":
        engine = JuniorScoringEngine()
        report = engine.evaluate(student_info, responses)
    else:
        engine = SeniorScoringEngine()
        report = engine.evaluate(student_info, responses)
    
    # Calibrate exact metrics from submission
    report.student.name = student_name
    report.student.student_class = student_class
    report.student.academic_score = f"{academic_pct}%"
    report.student.assessment_date = created_at
    
    if "consistency_risk" in record:
        report.consistency_risk = record["consistency_risk"]
    
    # Performance Snapshot overrides
    perf = record.get("performance", {})
    if perf:
        report.performance.analytical_thinking = perf.get("analytical_thinking", academic_pct)
        report.performance.creativity = perf.get("creativity", record.get("idea_score", 85))
        report.performance.consistency = perf.get("consistency", record.get("consistency_score", 40))
        report.performance.discipline = perf.get("discipline", int(record.get("consistency_score", 40) * 0.9))
        report.performance.leadership_potential = perf.get("leadership_potential", 55)
        report.performance.emotional_control = perf.get("emotional_control", 50)
    
    # Behaviour Snapshot overrides
    beh = record.get("behaviour", {})
    if beh:
        report.behaviour.start_enthusiasm = beh.get("start_enthusiasm", record.get("idea_score", 85))
        report.behaviour.task_completion = beh.get("task_completion", record.get("completion_score", 30))
        report.behaviour.planning_strength = beh.get("planning_strength", int(academic_pct * 0.85))
        report.behaviour.mid_task_follow_through = beh.get("mid_task_follow_through", record.get("completion_score", 30))
        report.behaviour.self_correction = beh.get("self_correction", 65)
        report.behaviour.conflict_handling = beh.get("conflict_handling", 45)

    # Execution Funnel
    idea_val = record.get("idea_score", 90)
    comp_val = record.get("completion_score", 30)
    report.execution_funnel.idea_generation = idea_val
    report.execution_funnel.task_completion_rate = comp_val
    report.execution_funnel.initial_execution = int((idea_val + comp_val) / 2)
    report.execution_funnel.mid_task_follow_through = comp_val

    # Custom strengths and risks if present
    custom_strengths = record.get("strengths")
    if custom_strengths and isinstance(custom_strengths, list) and len(custom_strengths) > 0:
        report.strengths = [
            StrengthItem(
                code=f"S-0{i+1}",
                title=s.split(":", 1)[-1].strip() if ":" in s else s,
                description=s,
                tag="KEY STRENGTH" if i < 3 else "RARE TRAIT"
            ) for i, s in enumerate(custom_strengths[:7])
        ]

    custom_risks = record.get("risks")
    if custom_risks and isinstance(custom_risks, list) and len(custom_risks) > 0:
        report.risks = [
            RiskItem(
                code=f"R-0{i+1}",
                title=r.split(":", 1)[-1].strip() if ":" in r else r,
                description=r,
                severity="HIGH RISK" if i < 2 else "MEDIUM"
            ) for i, r in enumerate(custom_risks[:6])
        ]

    if record.get("notes"):
        report.personality_quote = record.get("notes")
        
    return report

async def render_report_to_pdf(report: EvaluationReport, output_filename: str = "Shardul_Jadhao_Psychometric_Report.pdf") -> str:
    """Renders report Jinja2 template and generates A4 PDF via Playwright."""
    from playwright.async_api import async_playwright

    output_path = OUTPUT_DIR / output_filename
    
    # 1. Render HTML with base64 logo
    template = env.get_template("report_senior.html")
    rendered_html = template.render(
        report=report,
        logo_base64=get_logo_base64()
    )

    # 2. Convert to PDF using Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_content(rendered_html, wait_until="networkidle")
        await page.pdf(
            path=str(output_path),
            format="A4",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
        )
        await browser.close()

    return str(output_path)

if __name__ == "__main__":
    report = get_benchmark_shardul_report()
    pdf_file = asyncio.run(render_report_to_pdf(report))
    print(f"Generated benchmark PDF successfully: {pdf_file}")

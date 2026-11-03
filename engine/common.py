"""
Common models and utilities for Dodia Academy Psychometric Assessment Engine.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class StudentProfile(BaseModel):
    name: str = Field(..., description="Student full name")
    student_class: str = Field(..., description="Class e.g. Class IX, 9th Standard")
    academic_score: str = Field("85%", description="Academic score percentage or grade")
    assessment_type: str = Field("senior", description="'senior' (12-16) or 'junior' (4-11)")
    assessment_date: str = Field("May 2026", description="Month Year")
    assessor_name: str = Field("MR. TUSHAR DODIA", description="Assessor")
    assessor_title: str = Field("BE COMP [GOLD MEDALIST], MBA [FINANCE], CFA [USA], FRM [USA]", description="Credentials")
    assessor_phone: str = Field("7741823212", description="Contact phone")
    
    # Family Details
    father_name: Optional[str] = ""
    father_occupation: Optional[str] = ""
    father_qualification: Optional[str] = ""
    mother_name: Optional[str] = ""
    mother_occupation: Optional[str] = ""
    mother_qualification: Optional[str] = ""

class PerformanceSnapshot(BaseModel):
    analytical_thinking: int = 72
    creativity: int = 58
    consistency: int = 30
    discipline: int = 40
    leadership_potential: int = 50
    emotional_control: int = 55

class BehaviourSnapshot(BaseModel):
    start_enthusiasm: int = 85
    task_completion: int = 35
    planning_strength: int = 70
    mid_task_follow_through: int = 32
    self_correction: int = 65
    conflict_handling: int = 38

class ExecutionFunnel(BaseModel):
    idea_generation: int = 92
    planning_strategy: int = 65
    initial_execution: int = 60
    mid_task_follow_through: int = 30
    task_completion_rate: int = 28

class StrengthItem(BaseModel):
    code: str  # S-01
    title: str
    description: str
    tag: str = "KEY STRENGTH"  # "KEY STRENGTH" or "RARE TRAIT"

class RiskItem(BaseModel):
    code: str  # R-01
    title: str
    description: str
    severity: str = "HIGH RISK"  # "HIGH RISK", "MEDIUM-HIGH", "MEDIUM"

class RedFlagItem(BaseModel):
    severity: str = "HIGH"  # "HIGH", "MEDIUM"
    title: str
    description: str

class MindsetShift(BaseModel):
    avoid_quote: str
    adopt_quote: str

class CareerFitItem(BaseModel):
    title: str
    subtext: str
    fit_level: str  # "HIGH FIT", "GOOD FIT", "MODERATE FIT"

class ActionPlanItem(BaseModel):
    frequency: str  # DAILY, WEEKLY, MINDSET, SKILL DEV
    focus_area: str
    action_steps: str
    purpose: str

class EvaluationReport(BaseModel):
    student: StudentProfile
    potential_rating: str = "Moderate"
    consistency_risk: str = "High"
    header_tagline: str = "Thinking strength present — Execution and consistency gap is the real problem."
    learning_style: str = "Auditory (Listening) + Hands-On Try"
    behaviour_pattern: str = "Strong Start · Inconsistent Execution"
    
    personality_title: str = "Thinking strength present — Execution and Consistency Gap is the Real Problem"
    personality_desc_hindi: str = "तेज़ सोच है, concept जल्दी समझता है — लेकिन consistency और long-term follow-through अभी कमज़ोर है।"
    personality_quote: str = "दिमाग ठीक है — लेकिन काम शुरू करके छोड़ देने की आदत सबसे बड़ा खतरा है।"
    
    performance: PerformanceSnapshot = Field(default_factory=PerformanceSnapshot)
    behaviour: BehaviourSnapshot = Field(default_factory=BehaviourSnapshot)
    
    hidden_traits: List[str] = Field(default_factory=list)
    communication_style: List[str] = Field(default_factory=list)
    internal_dialogue: str = "अगर result अच्छा है तो मैं अच्छा हूँ"
    
    strengths: List[StrengthItem] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    
    execution_funnel: ExecutionFunnel = Field(default_factory=ExecutionFunnel)
    execution_quote: str = "यह student एक Starter है — Finisher नहीं। यही Gap address करना है।"
    red_flags: List[RedFlagItem] = Field(default_factory=list)
    
    mindset_shifts: List[MindsetShift] = Field(default_factory=list)
    
    career_inclination_summary: str = "Natural Inclination: Analytical + Physical + Logical — Thinking-driven है, rote-learning वाला नहीं। Repetitive या mechanical काम इसे demotivate करेगा।"
    best_fit_careers: List[CareerFitItem] = Field(default_factory=list)
    not_suitable_careers: List[str] = Field(default_factory=list)
    
    action_plan: List[ActionPlanItem] = Field(default_factory=list)
    
    final_verdict_quote: str = "Capable but under-performing — The gap between potential and performance is the only real problem."
    if_no_improvement: List[str] = Field(default_factory=list)
    if_corrected_now: List[str] = Field(default_factory=list)
    
    personal_letter_student_name: str = "Shardul"
    personal_letter_content: str = ""
    personal_letter_signoff: str = "शुरुआत strong करो — और इस बार Finish भी करो।"

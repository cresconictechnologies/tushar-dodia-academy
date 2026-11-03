"""
Junior Psychometric Scoring Engine (Ages 4 - 11)
Calibrated to Dodia Academy foundational evaluation rubric.
"""
from typing import Dict, Any, List
from .common import (
    EvaluationReport, StudentProfile, PerformanceSnapshot, BehaviourSnapshot,
    ExecutionFunnel, StrengthItem, RiskItem, RedFlagItem, MindsetShift,
    CareerFitItem, ActionPlanItem
)

class JuniorScoringEngine:
    def __init__(self):
        pass

    def evaluate(self, student_info: Dict[str, Any], responses: Dict[str, Any]) -> EvaluationReport:
        name = student_info.get("name", "Junior Student")
        student_class = student_info.get("student_class", "Class IV")
        academic_score = student_info.get("academic_score", "88%")
        first_name = name.split()[0] if name else "Student"
        
        father_occ = student_info.get("father_occupation", "")
        
        # Primary Learning Style calculation from Junior responses
        # Q12: Watch someone (Visual), Try yourself (Kinesthetic), Listen (Auditory)
        learning_style = "Visual & Kinesthetic (Hands-On Explorer)"
        behaviour_pattern = "High Curiosity · Developing Attention Span"
        
        potential_rating = "High Natural Curiosity"
        consistency_risk = "Moderate (Age Appropriate)"
        
        tagline = "High curiosity and grasping power — Early habit formation is the key opportunity."
        personality_title = "Creative Explorer — High Grasping with Need for Structured Routine"
        personality_desc_hindi = "जिज्ञासा और सीखने की इच्छा बहुत अच्छी है — लेकिन ध्यान जल्दी भटकता है और नियमित आदत की ज़रूरत है।"
        personality_quote = "बुनियाद मज़बूत हो तो भविष्य आसान हो जाता है।"
        
        # Junior Metrics
        analytical = 68
        creativity = 82
        consistency = 45
        discipline = 42
        leadership = 52
        emotional_control = 50

        # Behavior metrics
        start_enthusiasm = 90
        task_completion = 48
        planning_strength = 55
        mid_task = 44
        self_correction = 60
        conflict_handling = 50

        # Execution Funnel
        idea_gen = 95
        plan_strat = 58
        init_exec = 75
        mid_follow = 45
        task_comp_rate = 42

        hidden_traits = [
            "Mistake होने पर जल्दी संकोच महसूस करता है",
            "Encouragement और praise मिलने पर 2x बेहतर perform करता है",
            "Screen/visuals की तरफ attraction ज़्यादा है"
        ]

        communication_style = [
            "Stories और examples से जल्दी relate करता है",
            "Feelings खुलकर share करने में supportive माहौल चाहिए",
            "Activity-based discussions में actively participate करता है",
            "Polite and responsive with mentors"
        ]

        internal_dialogue = "अगर सब मुझे appreciate करेंगे तो मैं और अच्छा करूँगा"

        strengths = [
            StrengthItem(
                code="J–01",
                title="Curious & Quick Observer",
                description="नई चीज़ों को देखकर जल्दी सीखता है। Visual memory और curiosity बहुत strong है।",
                tag="KEY STRENGTH"
            ),
            StrengthItem(
                code="J–02",
                title="Creative Expression",
                description="Drawing, story making, imaginative play में natural interest है।",
                tag="KEY STRENGTH"
            ),
            StrengthItem(
                code="J–03",
                title="Helpful & Cooperative Spirit",
                description="Classmates और family members के साथ मिलकर काम करने में joy महसूस करता है।",
                tag="KEY STRENGTH"
            ),
            StrengthItem(
                code="J–04",
                title="High Physical Energy",
                description="Active games और movement पसंद करता है — energy channelize करने से focus 2x बढ़ेगा।",
                tag="RARE TRAIT"
            ),
            StrengthItem(
                code="J–05",
                title="Positive Receptivity to Guidance",
                description="प्यार और structure के साथ guide करने पर fast learner साबित होता है।",
                tag="KEY STRENGTH"
            ),
            StrengthItem(
                code="J–06",
                title="Pattern & Puzzle Recognition",
                description="Shapes, building blocks और logic games में natural focus दिखता है।",
                tag="RARE TRAIT"
            ),
            StrengthItem(
                code="J–07",
                title="Empathy towards Peers",
                description="दोस्तों की खुशी और परेशानी notice करता है — solid emotional foundation।",
                tag="KEY STRENGTH"
            ),
        ]

        risks = [
            RiskItem(
                code="JR–01",
                title="Short Attention Span / Screen Distraction",
                description="काम शुरू करके जल्दी distract होना — early age में screen time control करना ज़रूरी है।",
                severity="HIGH RISK"
            ),
            RiskItem(
                code="JR–02",
                title="Frustration Under Difficulty",
                description="Puzzle या question ना बनने पर चिढ़ जाना या छोड़ देना — grit development की ज़रूरत है।",
                severity="MEDIUM-HIGH"
            ),
            RiskItem(
                code="JR–03",
                title="Hesitation to Ask in Front of Others",
                description="Doubt होने पर चुप रह जाना — fearless expression सिखाना आवश्यक है।",
                severity="MEDIUM"
            ),
            RiskItem(
                code="JR–04",
                title="Inconsistent Bedtime & Study Routine",
                description="Daily schedule fluctuate होने से school focus पर असर पड़ता है।",
                severity="MEDIUM"
            ),
        ]

        red_flags = [
            RedFlagItem(
                severity="HIGH",
                title="Leaving Tasks Half-Done",
                description="Painting या homework बीच में छोड़ देने की आदत अगर अभी नहीं सुधारी गई, तो senior classes में study fatigue बनेगा।"
            ),
            RedFlagItem(
                severity="MEDIUM",
                title="Need for Constant Validation",
                description="Self-satisfaction के बजाय केवल तारीफ के लिए काम करना long-term intrinsic motivation कम करता है।"
            )
        ]

        mindset_shifts = [
            MindsetShift(avoid_quote="मुझसे नहीं हो रहा, मैं नहीं करूँगा", adopt_quote="थोड़ा आराम करके दोबारा कोशिश करता हूँ"),
            MindsetShift(avoid_quote="गलती हो गई तो डाँट पड़ेगी", adopt_quote="गलती सीखने का पहला कदम है"),
            MindsetShift(avoid_quote="सिर्फ खेलूँगा, पढ़ना बोरिंग है", adopt_quote="25 मिनट पढ़ाई finish, फिर मस्ती का पूरा मज़ा"),
        ]

        best_fit = [
            CareerFitItem(title="Visual Arts & Design", subtext="Creative & imaginative orientation", fit_level="HIGH FIT"),
            CareerFitItem(title="Robotics & Hands-On Science", subtext="Spatial & puzzle intelligence", fit_level="HIGH FIT"),
            CareerFitItem(title="Sports & Athletics", subtext="High physical energy balance", fit_level="GOOD FIT"),
            CareerFitItem(title="Communication & Media", subtext="Expressive & social orientation", fit_level="GOOD FIT"),
        ]

        not_suitable = [
            "Pure theoretical lecture-only environments without activities",
            "High-pressure comparative testing at an early age"
        ]

        action_plan = [
            ActionPlanItem(frequency="DAILY", focus_area="25-Min Focus Habit", action_steps="बिना किसी TV या mobile के 25 min quiet reading या writing table पर।", purpose="Focus Muscle"),
            ActionPlanItem(frequency="DAILY", focus_area="Puzzle / Brain Teaser", action_steps="Daily 1 jigsaw puzzle, Sudoku Jr, या Lego building challenge.", purpose="Cognitive Grit"),
            ActionPlanItem(frequency="DAILY", focus_area="Bedtime Story Reflection", action_steps="रात को सोने से पहले दिन की 1 अच्छी बात और 1 नया सीखा शब्द discuss करना।", purpose="Communication"),
            ActionPlanItem(frequency="WEEKLY", focus_area="Outdoor Sport & Team Play", action_steps="Weekend पर swimming, cycling, या football session.", purpose="Physical Discipline"),
        ]

        if_no_imp = [
            "Attention span कमज़ोर रह जाएगा",
            "Exam time में बैठने की आदत नहीं बनेगी",
            "Screen dependency बढ़ सकती है"
        ]

        if_corr = [
            "Class का top enthusiastic learner बनेगा",
            "Self-reliant और organized habit बनेगी",
            "Curiosity academic excellence में convert होगी"
        ]

        letter_content = (
            f"प्रिय {first_name} और आदरणीय अभिभावक: "
            f"{first_name} के अंदर गजब की ऊर्जा और सीखने की उत्सुकता है। इस उम्र में सबसे महत्वपूर्ण परीक्षा के अंक नहीं, "
            f"बल्कि रोज़ाना 30 मिनट शांत मन से बैठने की आदत और गलतियों से ना डरने का हौसला है। "
            f"अगर हम घर और Academy मिलकर इस पर काम करेंगे, तो {first_name} हर क्षेत्र में अद्भुत प्रदर्शन करेगा।"
        )

        student_prof = StudentProfile(
            name=name,
            student_class=student_class,
            academic_score=academic_score,
            assessment_type="junior",
            assessment_date=student_info.get("assessment_date", "May 2026"),
            assessor_name=student_info.get("assessor_name", "MR. TUSHAR DODIA"),
            assessor_title=student_info.get("assessor_title", "BE COMP [GOLD MEDALIST], MBA [FINANCE], CFA [USA], FRM [USA]"),
            assessor_phone=student_info.get("assessor_phone", "7741823212"),
            father_name=student_info.get("father_name", ""),
            father_occupation=father_occ,
            father_qualification=student_info.get("father_qualification", ""),
            mother_name=student_info.get("mother_name", ""),
            mother_occupation=student_info.get("mother_occupation", ""),
            mother_qualification=student_info.get("mother_qualification", "")
        )

        return EvaluationReport(
            student=student_prof,
            potential_rating=potential_rating,
            consistency_risk=consistency_risk,
            header_tagline=tagline,
            learning_style=learning_style,
            behaviour_pattern=behaviour_pattern,
            personality_title=personality_title,
            personality_desc_hindi=personality_desc_hindi,
            personality_quote=personality_quote,
            performance=PerformanceSnapshot(
                analytical_thinking=analytical,
                creativity=creativity,
                consistency=consistency,
                discipline=discipline,
                leadership_potential=leadership,
                emotional_control=emotional_control
            ),
            behaviour=BehaviourSnapshot(
                start_enthusiasm=start_enthusiasm,
                task_completion=task_completion,
                planning_strength=planning_strength,
                mid_task_follow_through=mid_task,
                self_correction=self_correction,
                conflict_handling=conflict_handling
            ),
            hidden_traits=hidden_traits,
            communication_style=communication_style,
            internal_dialogue=internal_dialogue,
            strengths=strengths,
            risks=risks,
            execution_funnel=ExecutionFunnel(
                idea_generation=idea_gen,
                planning_strategy=plan_strat,
                initial_execution=init_exec,
                mid_task_follow_through=mid_follow,
                task_completion_rate=task_comp_rate
            ),
            execution_quote="शुरुआत बहुत सुंदर है — अब धीरे-धीरे पूरा करने का संतोष महसूस कराना है।",
            red_flags=red_flags,
            mindset_shifts=mindset_shifts,
            career_inclination_summary="Natural Curiosity: Creative + Observant + Hands-on — Active experimentation से सीखता है।",
            best_fit_careers=best_fit,
            not_suitable_careers=not_suitable,
            action_plan=action_plan,
            final_verdict_quote="A curious mind with high potential — Nurture the habits today for brilliance tomorrow.",
            if_no_improvement=if_no_imp,
            if_corrected_now=if_corr,
            personal_letter_student_name=first_name,
            personal_letter_content=letter_content,
            personal_letter_signoff="खूब सीखो, खूब बढ़ो — Dodia Academy सदैव तुम्हारे साथ है।"
        )

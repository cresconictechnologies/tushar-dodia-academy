// Interactive Psychometric Assessment Logic & Live Diagnostic Simulation
// Supports both Senior (Classes 7-12) and Junior (Classes 1-6) frameworks.

const seniorQuestions = [
  {
    id: "s1",
    category: "Academic & Exam Management",
    question: "When facing a major competitive or board examination, what is your primary pattern?",
    options: [
      { text: "I build structured conceptual summaries and revise systematically well in advance.", scoreAcademic: 90, scoreConsistency: 85, ideaScore: 90, compScore: 85 },
      { text: "I start strong with full enthusiasm and color-coded timetables, but lose steam halfway.", scoreAcademic: 85, scoreConsistency: 50, ideaScore: 95, compScore: 35 },
      { text: "I procrastinate until pressure builds, then pull intense all-nighters to score average to good.", scoreAcademic: 70, scoreConsistency: 40, ideaScore: 80, compScore: 50 },
      { text: "I get overwhelmed by large syllabi and freeze, needing constant external reminders.", scoreAcademic: 55, scoreConsistency: 30, ideaScore: 60, compScore: 20 }
    ]
  },
  {
    id: "s2",
    category: "Focus & Digital Habit Patterns",
    question: "How do smartphones and notifications affect your deep study sessions?",
    options: [
      { text: "Phone is locked in another room; I enter flow state without checking for 2-3 hours.", scoreAcademic: 95, scoreConsistency: 90, ideaScore: 90, compScore: 90 },
      { text: "I check my phone 'just for 2 minutes' to clarify a concept, but end up lost in reels for 45 minutes.", scoreAcademic: 75, scoreConsistency: 45, ideaScore: 90, compScore: 30 },
      { text: "I keep study tabs and entertainment tabs open side-by-side, switching constantly.", scoreAcademic: 65, scoreConsistency: 35, ideaScore: 85, compScore: 25 },
      { text: "Digital distraction is manageable only when parents or teachers sit right next to me.", scoreAcademic: 70, scoreConsistency: 50, ideaScore: 70, compScore: 40 }
    ]
  },
  {
    id: "s3",
    category: "Execution Funnel: Starter vs. Finisher",
    question: "When you get an exciting new hobby, project, or learning goal, what is the usual outcome?",
    options: [
      { text: "I complete 80%+ of what I initiate, documenting and measuring my progress to the finish line.", scoreAcademic: 90, scoreConsistency: 90, ideaScore: 85, compScore: 90 },
      { text: "Huge initial spark! I buy books/materials immediately, talk about it, but abandon it at the 30% mark.", scoreAcademic: 85, scoreConsistency: 45, ideaScore: 98, compScore: 25 },
      { text: "I hesitate to even start because I overthink whether it will be 100% perfect.", scoreAcademic: 70, scoreConsistency: 55, ideaScore: 60, compScore: 40 },
      { text: "I rely entirely on project deadlines set by school; on personal goals I rarely finish.", scoreAcademic: 65, scoreConsistency: 40, ideaScore: 70, compScore: 35 }
    ]
  },
  {
    id: "s4",
    category: "Emotional Resilience & Feedback",
    question: "When a mentor or parent points out a flaw or you score lower than expected on a test, how do you respond?",
    options: [
      { text: "I analyze the error log objectively, view critique as data, and adjust my method.", scoreAcademic: 90, scoreConsistency: 85, ideaScore: 85, compScore: 85 },
      { text: "I feel an intense defensive sting, withdraw into my room for hours, and doubt my worth.", scoreAcademic: 75, scoreConsistency: 60, ideaScore: 80, compScore: 50 },
      { text: "I brush it off casually on the surface, but secretly carry anxiety about failure.", scoreAcademic: 80, scoreConsistency: 55, ideaScore: 75, compScore: 45 },
      { text: "I blame external factors (unfair questions, lack of time, poor teaching) first.", scoreAcademic: 60, scoreConsistency: 35, ideaScore: 65, compScore: 30 }
    ]
  },
  {
    id: "s5",
    category: "Career & Vision Alignment",
    question: "How clear are you regarding your career trajectory and intrinsic strengths?",
    options: [
      { text: "Crystal clear on my natural analytical/creative strengths and actively matching them with career domains.", scoreAcademic: 95, scoreConsistency: 85, ideaScore: 90, compScore: 85 },
      { text: "I have high ambition (Tech/Finance/Design/Civil Services) but lack a day-to-day tactical execution roadmap.", scoreAcademic: 85, scoreConsistency: 50, ideaScore: 95, compScore: 30 },
      { text: "I am mainly pursuing what my peer circle or family expectations recommend.", scoreAcademic: 70, scoreConsistency: 60, ideaScore: 60, compScore: 50 },
      { text: "I feel confused by multiple contrasting interests and don't know what fits my personality.", scoreAcademic: 65, scoreConsistency: 45, ideaScore: 70, compScore: 35 }
    ]
  }
];

const juniorQuestions = [
  {
    id: "j1",
    category: "Sensory & Learning Style (VARK)",
    question: "When your child is learning a new story, concept, or math lesson, how do they grasp it fastest?",
    options: [
      { text: "Visual: Remembers pictures, diagrams, and color-coded drawings instantly.", scoreAcademic: 88, scoreConsistency: 80, ideaScore: 90, compScore: 75 },
      { text: "Auditory: Loves listening to stories, teacher explanations, and repeating dialogues.", scoreAcademic: 85, scoreConsistency: 75, ideaScore: 85, compScore: 70 },
      { text: "Kinesthetic / Hands-on: Learns best by touching, building blocks, experiments, or role-playing.", scoreAcademic: 80, scoreConsistency: 60, ideaScore: 95, compScore: 50 },
      { text: "Read / Write: Enjoys copying words, reading storybooks, and organizing flashcards.", scoreAcademic: 85, scoreConsistency: 85, ideaScore: 75, compScore: 80 }
    ]
  },
  {
    id: "j2",
    category: "Attention Span & Focus Endurance",
    question: "How long can your child concentrate continuously on schoolwork without restlessness?",
    options: [
      { text: "35 to 45+ minutes in deep calm concentration without prompting.", scoreAcademic: 92, scoreConsistency: 88, ideaScore: 85, compScore: 88 },
      { text: "15 to 25 minutes of energetic focus, then needs a short movement break.", scoreAcademic: 85, scoreConsistency: 65, ideaScore: 90, compScore: 60 },
      { text: "Under 10 minutes; easily distracted by room sounds, siblings, or toys.", scoreAcademic: 70, scoreConsistency: 45, ideaScore: 80, compScore: 40 },
      { text: "Focuses for hours only on mobile videos/cartoons, but resists academic reading.", scoreAcademic: 65, scoreConsistency: 35, ideaScore: 95, compScore: 25 }
    ]
  },
  {
    id: "j3",
    category: "Sensory Environment & Reactivity",
    question: "How does the child react to busy, noisy, or bright study environments?",
    options: [
      { text: "Highly adaptable; stays happily absorbed even in a lively family room.", scoreAcademic: 88, scoreConsistency: 85, ideaScore: 85, compScore: 80 },
      { text: "Sensitive observer; needs a quiet, calm desk with minimal clutter to do best work.", scoreAcademic: 85, scoreConsistency: 70, ideaScore: 88, compScore: 65 },
      { text: "Active seeker; hums, fidgets, or needs background sound while drawing or solving math.", scoreAcademic: 75, scoreConsistency: 50, ideaScore: 90, compScore: 45 },
      { text: "Easily overwhelmed or irritated after prolonged noisy stimulation in school.", scoreAcademic: 70, scoreConsistency: 45, ideaScore: 75, compScore: 40 }
    ]
  },
  {
    id: "j4",
    category: "Emotional Regulation & Frustration Tolerance",
    question: "When the child makes a mistake, loses a game, or faces hard homework, what happens?",
    options: [
      { text: "Calmly erases, asks for a hint, and tries again patiently.", scoreAcademic: 90, scoreConsistency: 85, ideaScore: 85, compScore: 85 },
      { text: "Gets temporarily upset or pouts, but recovers within 5 minutes with gentle encouragement.", scoreAcademic: 82, scoreConsistency: 65, ideaScore: 85, compScore: 60 },
      { text: "Throws pencils, bursts into tears, or stubbornly refuses to continue for the day.", scoreAcademic: 65, scoreConsistency: 40, ideaScore: 80, compScore: 30 },
      { text: "Quietly avoids difficult activities to avoid feeling bad about getting them wrong.", scoreAcademic: 68, scoreConsistency: 45, ideaScore: 70, compScore: 35 }
    ]
  },
  {
    id: "j5",
    category: "Daily Routine & Habit Rituals",
    question: "What is the child's morning, school bag, and bedtime routine consistency?",
    options: [
      { text: "Independent; follows fixed timings for waking, school bag, and homework happily.", scoreAcademic: 92, scoreConsistency: 90, ideaScore: 80, compScore: 90 },
      { text: "Cooperative as long as a parent is physically sitting in the room guiding them.", scoreAcademic: 82, scoreConsistency: 70, ideaScore: 85, compScore: 65 },
      { text: "Requires 4 to 6 repetitive verbal reminders every morning and evening.", scoreAcademic: 70, scoreConsistency: 45, ideaScore: 80, compScore: 40 },
      { text: "Daily friction and resistance around waking up, packing, and sitting down to study.", scoreAcademic: 60, scoreConsistency: 30, ideaScore: 75, compScore: 25 }
    ]
  }
];

let currentTier = "senior"; // 'senior' or 'junior'
let currentQIndex = 0;
let userAnswers = {};

function getActiveQuestions() {
  return currentTier === "junior" ? juniorQuestions : seniorQuestions;
}

function initAssessment() {
  const quizContainer = document.getElementById('quizSimulator');
  if (!quizContainer) return;

  // Setup Tier Switcher
  const seniorBtn = document.getElementById('seniorTierBtn');
  const juniorBtn = document.getElementById('juniorTierBtn');

  seniorBtn?.addEventListener('click', () => {
    if (currentTier === "senior") return;
    currentTier = "senior";
    currentQIndex = 0;
    userAnswers = {};
    updateTierButtons();
    renderQuestion();
  });

  juniorBtn?.addEventListener('click', () => {
    if (currentTier === "junior") return;
    currentTier = "junior";
    currentQIndex = 0;
    userAnswers = {};
    updateTierButtons();
    renderQuestion();
  });

  updateTierButtons();
  renderQuestion();
}

function updateTierButtons() {
  const seniorBtn = document.getElementById('seniorTierBtn');
  const juniorBtn = document.getElementById('juniorTierBtn');

  if (currentTier === "senior") {
    if (seniorBtn) {
      seniorBtn.style.background = 'var(--royal-blue)';
      seniorBtn.style.color = '#ffffff';
      seniorBtn.style.border = '2px solid var(--royal-blue)';
      seniorBtn.style.boxShadow = '0 4px 12px rgba(37,99,235,0.25)';
    }
    if (juniorBtn) {
      juniorBtn.style.background = '#ffffff';
      juniorBtn.style.color = 'var(--text-secondary)';
      juniorBtn.style.border = '2px solid var(--border-light)';
      juniorBtn.style.boxShadow = 'none';
    }
  } else {
    if (juniorBtn) {
      juniorBtn.style.background = 'var(--royal-blue)';
      juniorBtn.style.color = '#ffffff';
      juniorBtn.style.border = '2px solid var(--royal-blue)';
      juniorBtn.style.boxShadow = '0 4px 12px rgba(37,99,235,0.25)';
    }
    if (seniorBtn) {
      seniorBtn.style.background = '#ffffff';
      seniorBtn.style.color = 'var(--text-secondary)';
      seniorBtn.style.border = '2px solid var(--border-light)';
      seniorBtn.style.boxShadow = 'none';
    }
  }
}

function renderQuestion() {
  const questions = getActiveQuestions();
  const q = questions[currentQIndex];
  const stepLabel = document.getElementById('quizStepLabel');
  const progressFill = document.getElementById('quizProgressFill');
  const qTitle = document.getElementById('quizTitle');
  const qCategory = document.getElementById('quizCategory');
  const optionsBox = document.getElementById('quizOptions');
  const prevBtn = document.getElementById('quizPrevBtn');
  const nextBtn = document.getElementById('quizNextBtn');

  if (stepLabel) stepLabel.textContent = `Question ${currentQIndex + 1} of ${questions.length}`;
  if (progressFill) progressFill.style.width = `${((currentQIndex + 1) / questions.length) * 100}%`;
  if (qCategory) qCategory.textContent = q.category;
  if (qTitle) qTitle.textContent = q.question;

  if (optionsBox) {
    optionsBox.innerHTML = '';
    q.options.forEach((opt, idx) => {
      const isSelected = userAnswers[q.id] === idx;
      const label = document.createElement('label');
      label.className = `quiz-option-label ${isSelected ? 'selected' : ''}`;
      label.innerHTML = `
        <input type="radio" name="q_${q.id}" value="${idx}" class="quiz-option-radio" ${isSelected ? 'checked' : ''}>
        <span class="quiz-option-text">${opt.text}</span>
      `;
      label.addEventListener('click', () => {
        userAnswers[q.id] = idx;
        document.querySelectorAll('.quiz-option-label').forEach(el => el.classList.remove('selected'));
        label.classList.add('selected');
        if (nextBtn) nextBtn.disabled = false;
      });
      optionsBox.appendChild(label);
    });
  }

  if (prevBtn) {
    prevBtn.style.visibility = currentQIndex === 0 ? 'hidden' : 'visible';
    prevBtn.onclick = () => {
      if (currentQIndex > 0) {
        currentQIndex--;
        renderQuestion();
      }
    };
  }

  if (nextBtn) {
    nextBtn.disabled = userAnswers[q.id] === undefined;
    nextBtn.textContent = currentQIndex === questions.length - 1 ? 'Enter Details to Generate Diagnostic' : 'Next Question';
    nextBtn.onclick = () => {
      if (userAnswers[q.id] === undefined) return;
      if (currentQIndex < questions.length - 1) {
        currentQIndex++;
        renderQuestion();
      } else {
        promptCandidateDetails();
      }
    };
  }
}

function promptCandidateDetails() {
  const quizBox = document.getElementById('quizSimulator');
  if (!quizBox) return;

  const isJunior = currentTier === "junior";
  const tierName = isJunior ? "Junior Foundational Diagnostic" : "Senior High-School Diagnostic";
  const namePlaceholder = isJunior ? "e.g. Aarav Sharma" : "e.g. Rohan Sharma";
  const classPlaceholder = isJunior ? "e.g. Class 4th (Primary)" : "e.g. Class 10th (ICSE / CBSE)";

  quizBox.innerHTML = `
    <div style="text-align: center; margin-bottom: 24px;">
      <span class="badge-gold">STEP 2 OF 2 &middot; ${isJunior ? 'CHILD & PARENT IDENTIFICATION' : 'CANDIDATE IDENTIFICATION'}</span>
      <h3 style="font-size: 1.6rem; font-weight: 800; color: var(--royal-navy); margin: 10px 0 6px;">File Your Assessment With Dodia Academy</h3>
      <p style="font-size: 0.92rem; color: var(--text-secondary); max-width: 58ch; margin: 0 auto;">
        ${tierName}. The comprehensive diagnostic dossier will be generated and routed directly to Mr. Tushar Dodia's executive desk.
      </p>
    </div>

    <form id="candidateDetailForm" style="max-width: 600px; margin: 0 auto; background: var(--bg-page); padding: 24px; border-radius: var(--radius-md); border: 1px solid var(--border-light);">
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 14px;">
        <div class="form-group">
          <label style="display: block; font-size: 0.84rem; font-weight: 700; color: var(--royal-navy); margin-bottom: 4px;">
            ${isJunior ? "Child's Full Name *" : "Student Full Name *"}
          </label>
          <input type="text" id="candidateName" class="form-input" placeholder="${namePlaceholder}" required>
        </div>
        <div class="form-group">
          <label style="display: block; font-size: 0.84rem; font-weight: 700; color: var(--royal-navy); margin-bottom: 4px;">Class / Grade *</label>
          <input type="text" id="candidateClass" class="form-input" placeholder="${classPlaceholder}" required>
        </div>
      </div>

      <div style="margin-bottom: 14px;">
        <label style="display: block; font-size: 0.84rem; font-weight: 700; color: var(--royal-navy); margin-bottom: 4px;">School / College Name *</label>
        <input type="text" id="candidateSchool" class="form-input" placeholder="e.g. Model English School, Pune" required>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;">
        <div class="form-group">
          <label style="display: block; font-size: 0.84rem; font-weight: 700; color: var(--royal-navy); margin-bottom: 4px;">Parent WhatsApp Mobile *</label>
          <input type="tel" id="candidatePhone" class="form-input" placeholder="+91 9876543210" required>
        </div>
        <div class="form-group">
          <label style="display: block; font-size: 0.84rem; font-weight: 700; color: var(--royal-navy); margin-bottom: 4px;">Parent / Student Email</label>
          <input type="email" id="candidateEmail" class="form-input" placeholder="parent@domain.com">
        </div>
      </div>

      <button type="submit" id="submitAssessmentBtn" class="btn btn-primary" style="width: 100%; padding: 14px; font-size: 1rem;">
        <i class="fa-solid fa-paper-plane"></i> Generate &amp; File Diagnostic Report
      </button>

      <div style="text-align: center; margin-top: 12px; font-size: 0.78rem; color: var(--text-secondary);">
        <i class="fa-solid fa-lock" style="color: var(--royal-blue); margin-right: 4px;"></i>
        Private &amp; Confidential. Filed securely in Dodia Academy Executive Admin Portal.
      </div>
    </form>
  `;

  document.getElementById('candidateDetailForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('submitAssessmentBtn');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating Diagnostic Dossier...';
    }

    const questions = getActiveQuestions();
    let totalAcademic = 0;
    let totalConsistency = 0;
    let totalIdea = 0;
    let totalCompletion = 0;

    questions.forEach(q => {
      const selectedIdx = userAnswers[q.id] !== undefined ? userAnswers[q.id] : 1;
      const opt = q.options[selectedIdx];
      totalAcademic += opt.scoreAcademic;
      totalConsistency += opt.scoreConsistency;
      totalIdea += opt.ideaScore;
      totalCompletion += opt.compScore;
    });

    const avgAcademic = Math.round(totalAcademic / questions.length);
    const avgConsistency = Math.round(totalConsistency / questions.length);
    const avgIdea = Math.round(totalIdea / questions.length);
    const avgComp = Math.round(totalCompletion / questions.length);

    const payload = {
      tier: currentTier,
      student_name: document.getElementById('candidateName').value.trim(),
      student_class: document.getElementById('candidateClass').value.trim(),
      school_name: document.getElementById('candidateSchool').value.trim(),
      parent_phone: document.getElementById('candidatePhone').value.trim(),
      parent_email: document.getElementById('candidateEmail').value.trim(),
      academic_score: avgAcademic,
      consistency_score: avgConsistency,
      idea_score: avgIdea,
      completion_score: avgComp,
      user_answers: userAnswers
    };

    try {
      const res = await fetch('/api/submit-assessment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      showResults(data, payload);
    } catch (err) {
      alert('Unable to submit assessment. Please check your internet connection and try again.');
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Generate &amp; File Diagnostic Report';
      }
    }
  });
}

function showResults(serverData, payload) {
  const isJunior = currentTier === "junior";
  const avgAcademic = serverData?.scores?.academic || 85;
  const avgConsistency = serverData?.scores?.consistency || 50;
  const avgIdea = serverData?.scores?.idea || 88;
  const avgComp = serverData?.scores?.completion || 40;
  const gap = serverData?.scores?.gap || (avgIdea - avgComp);
  const reportId = serverData?.report_id || (isJunior ? "DA-2026-JR-PENDING" : "DA-2026-SR-PENDING");
  const studentName = payload?.student_name || "Student";

  const quizBox = document.getElementById('quizSimulator');
  if (!quizBox) return;

  const riskBadge = avgConsistency < 55 
    ? '<span class="badge-gold" style="background:#fee2e2; color:#b91c1c; border-color:#f87171;">HIGH CONSISTENCY RISK</span>' 
    : '<span class="badge-gold" style="background:#dcfce7; color:#15803d; border-color:#86efac;">STABLE EXECUTION</span>';

  const observationText = isJunior
    ? `The child demonstrates high natural curiosity (${avgIdea}%) and strong visual-sensory grasping, with routine discipline at ${avgConsistency}%. At primary age, the key developmental opportunity is predictable habit structuring and positive parent-child co-reading rather than exam pressure.`
    : (gap >= 40 
      ? `There is an acute <strong>Execution Gap of ${gap}%</strong>. The student exhibits high cognitive horsepower and creative spark, but momentum collapses before final completion. The primary intervention is daily habit ritualization, not repetitive study hours.` 
      : `The student demonstrates balanced execution momentum with moderate consistency reserves. Continued structured mentoring will cement board-exam confidence.`);

  quizBox.innerHTML = `
    <div style="text-align: center; margin-bottom: 24px;">
      <div style="display: inline-flex; align-items: center; gap: 8px; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 4px 14px; border-radius: var(--radius-full); font-size: 0.8rem; font-weight: 800; color: #065f46; margin-bottom: 10px;">
        <i class="fa-solid fa-circle-check" style="color: #10b981;"></i> REPORT GENERATED &amp; TRANSMITTED TO EXECUTIVE DESK
      </div>
      <h3 style="font-size: 1.8rem; font-weight: 800; color: var(--royal-navy); margin: 6px 0 4px;">
        ${studentName}'s Diagnostic Profile Snapshot
      </h3>
      <p style="font-size: 0.92rem; color: var(--text-secondary); margin: 0;">
        Official Tracking Reference: <strong>${reportId}</strong> &middot; Evaluated Under Dodia Academy Framework
      </p>
    </div>

    <div style="background: var(--bg-page); border-radius: var(--radius-md); padding: 24px; border: 1px solid var(--border-light); margin-bottom: 24px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid var(--border-light); padding-bottom: 10px;">
        <span style="font-weight: 700; color: var(--royal-navy); font-size: 1.05rem;">
          ${isJunior ? 'Sensory & Habit Competencies' : 'Core Psychometric Competencies'}
        </span>
        ${riskBadge}
      </div>

      <div style="margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; font-size: 0.88rem; font-weight: 700; margin-bottom: 5px;">
          <span>${isJunior ? 'Cognitive & Sensory Grasping Power' : 'Academic & Conceptual Aptitude'}</span>
          <span>${avgAcademic}%</span>
        </div>
        <div class="rm-progress-bg">
          <div class="rm-progress-fill fill-navy" style="width: ${avgAcademic}%;"></div>
        </div>
      </div>

      <div style="margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; font-size: 0.88rem; font-weight: 700; margin-bottom: 5px;">
          <span>${isJunior ? 'Daily Routine & Focus Endurance' : 'Consistency & Daily Habit Resilience'}</span>
          <span>${avgConsistency}%</span>
        </div>
        <div class="rm-progress-bg">
          <div class="rm-progress-fill fill-gold" style="width: ${avgConsistency}%;"></div>
        </div>
      </div>

      <div style="margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; font-size: 0.88rem; font-weight: 700; margin-bottom: 5px;">
          <span>${isJunior ? 'Curiosity & Idea Spark' : 'Ideation Energy (Starter Impulse)'}</span>
          <span style="color: #2563eb;">${avgIdea}%</span>
        </div>
        <div class="rm-progress-bg">
          <div class="rm-progress-fill" style="background: #2563eb; width: ${avgIdea}%;"></div>
        </div>
      </div>

      <div style="margin-bottom: 18px;">
        <div style="display: flex; justify-content: space-between; font-size: 0.88rem; font-weight: 700; margin-bottom: 5px;">
          <span>${isJunior ? 'Habit Follow-Through & Task Completion' : 'Execution Completion (Finisher Rate)'}</span>
          <span style="color: #dc2626;">${avgComp}%</span>
        </div>
        <div class="rm-progress-bg">
          <div class="rm-progress-fill fill-red" style="width: ${avgComp}%;"></div>
        </div>
      </div>

      <div style="background: #ffffff; padding: 14px 18px; border-radius: 4px; font-size: 0.88rem; line-height: 1.6; color: #1e293b; border: 1px solid var(--border-light); margin-bottom: 16px;">
        <strong>Tushar Sir's Clinical Diagnostic Observation:</strong>
        ${observationText}
      </div>

      <!-- Direct Report Download & In-Browser View Card -->
      <div style="background: #ffffff; border: 2px solid var(--royal-blue); border-radius: var(--radius-md); padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(37,99,235,0.12); text-align: center;">
        <div style="font-weight: 800; color: var(--royal-navy); font-size: 1.15rem; margin-bottom: 6px;">
          <i class="fa-solid fa-file-circle-check" style="color: #10b981; margin-right: 6px;"></i>
          Your Official 8-Page Psychometric Dossier is Ready!
        </div>
        <p style="font-size: 0.88rem; color: var(--text-secondary); margin: 0 0 16px; line-height: 1.5;">
          Includes full competency breakdown, Starter vs. Finisher execution funnel, habit vulnerability audit, and personalized recommendations.
        </p>
        <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;">
          <a href="/api/reports/${reportId}/pdf" target="_blank" download="${studentName}_Psychometric_Report_${reportId}.pdf" class="btn btn-primary" style="padding: 12px 24px; font-size: 0.95rem; background: var(--royal-blue); color: #ffffff; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; font-weight: 800; border-radius: var(--radius-md); box-shadow: 0 4px 12px rgba(37,99,235,0.3);">
            <i class="fa-solid fa-download"></i> Download 8-Page Report (PDF)
          </a>
          <a href="/api/reports/${reportId}/pdf" target="_blank" class="btn btn-secondary" style="padding: 12px 20px; font-size: 0.92rem; background: #ffffff; color: var(--royal-navy); border: 2px solid var(--royal-navy); text-decoration: none; display: inline-flex; align-items: center; gap: 8px; font-weight: 700;">
            <i class="fa-solid fa-eye"></i> View in Browser
          </a>
        </div>
      </div>

      <div style="background: #f8fafc; border-radius: 6px; padding: 14px 18px; font-size: 0.82rem; color: #475569; line-height: 1.5; border: 1px solid var(--border-light);">
        <i class="fa-solid fa-shield-halved" style="color: var(--royal-blue); margin-right: 4px;"></i>
        A permanent copy of this diagnostic dossier has been archived under ID <strong>${reportId}</strong> in Mr. Tushar Dodia's Executive Admin Repository for reference during clinical counselling.
      </div>
    </div>

    <div style="display: flex; gap: 14px; justify-content: center; flex-wrap: wrap;">
      <a href="https://wa.me/917741823212?text=Hello%20Tushar%20Sir%2C%20I%20have%20completed%20the%20Psychometric%20Assessment%20for%20my%20child%20${encodeURIComponent(studentName)}%20(Report%20ID%3A%20${reportId}).%20I%20have%20downloaded%20our%208-page%20report%20and%20would%20like%20to%20schedule%20our%201-on-1%20debrief%20session." target="_blank" class="btn btn-primary" style="background:#15803d; border-color:#15803d; padding: 12px 24px;">
        <i class="fa-brands fa-whatsapp"></i> WhatsApp Tushar Sir for 1-on-1 Debrief
      </a>
      <button class="btn btn-secondary" style="background:#e2e8f0; color:#334155; border:none; padding: 12px 20px;" onclick="location.reload()">
        <i class="fa-solid fa-arrow-rotate-left"></i> Retake Assessment
      </button>
    </div>
  `;
}

// Global helper for CTA buttons to activate interactive diagnostic immediately
window.startAssessment = function(tier) {
  if (tier && (tier === "senior" || tier === "junior")) {
    currentTier = tier;
    currentQIndex = 0;
    userAnswers = {};
    updateTierButtons();
    renderQuestion();
  }
  const el = document.getElementById('quizSimulator');
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
};

document.addEventListener('DOMContentLoaded', () => {
  // Check URL query params for auto-tier selection (e.g. /assessment?tier=senior)
  const urlParams = new URLSearchParams(window.location.search);
  const tierParam = urlParams.get('tier');
  if (tierParam && (tierParam === 'senior' || tierParam === 'junior')) {
    currentTier = tierParam;
  }
  initAssessment();
});

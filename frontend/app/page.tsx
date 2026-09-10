"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import Circuit from "@/components/Circuit";
import ModelGraph from "@/components/ModelGraph";
import InterventionFlow from "@/components/InterventionFlow";
import Navbar from "@/components/Navbar";
import { AuthState, apiFetch, getAuthState } from "@/lib/api";
import {
  Activity,
  ArrowRight,
  BadgeCheck,
  BrainCircuit,
  ChartNoAxesCombined,
  Check,
  ChevronRight,
  CircuitBoard,
  CloudCog,
  Cpu,
  Database,
  FlaskConical,
  Network,
  Play,
  Radio,
  RefreshCw,
  ScanSearch,
  ShieldCheck,
  Trash2,
  UserRound,
  Layers3,
  Sparkles,
  TrendingDown,
  Zap,
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Lang = "en" | "ar";
type View = "home" | "lab" | "insights" | "system";
type Stage = "diagnose" | "scan" | "experiment" | "result" | "intervention" | "verification" | "plan";

type Hypothesis = {
  id: string;
  name: string;
  probability: number;
};

type Diagnosis = {
  scan_id?: string | null;
  scenario_id?: string;
  parsed_reasoning: {
    summary: string;
    claims: string[];
    parser: string;
  };
  posterior: Record<string, number>;
  top_hypotheses: Hypothesis[];
  next_experiment: {
    id: string;
    name: string;
    description: string;
    prompt: string;
    options: string[];
    information_gain: number;
  };
};

type Simulation = {
  actual_outcome: string;
  measurements: Record<string, number>;
  explanation: string;
};

type ScenarioOption = {
  value: "A" | "B" | "same";
  label: string;
  label_ar: string;
};

type Scenario = {
  id: string;
  code: string;
  title: string;
  title_ar: string;
  question: string;
  question_ar: string;
  options: ScenarioOption[];
  sample_reasoning: string;
  sample_reasoning_ar: string;
  domain: "science" | "technology" | "engineering" | "mathematics";
  topic: string;
  circuit: { type: string; voltage: number; resistances: number[] };
  concepts: string[];
};

type ScanRecord = {
  id: string;
  createdAt: string;
  completedAt?: string | null;
  scenarioId: string;
  scenarioTitle: string;
  misconceptionId: string;
  misconception: string;
  before: number;
  after: number | null;
  experiment: string;
  informationGain: number;
  parser: string;
  completed: boolean;
};

type InsightsPayload = {
  totalScans: number;
  averageShift: number;
  largestShift: number;
  aggregated: { id: string; name: string; probability: number; observations: number }[];
  scenarioCoverage: { id: string; title: string; count: number }[];
  domainCoverage: { domain: string; count: number }[];
  interventionProgress: { completed: number; resolved: number; persistent: number; resolutionRate: number };
};

type PlatformStatus = {
  status: string;
  version: string;
  persistence: string;
  ai_provider: string;
  ai_model: string;
  physics_engine: string;
  scenario_count: number;
  misconception_count: number;
  evidence_engines?: string[];
};

const MISCONCEPTION_AR: Record<string, string> = {
  M1: "يتم استهلاك التيار أثناء مروره",
  M2: "الأقرب للبطارية يحصل على قدرة أكبر",
  M3: "البطارية ترسل تيارًا ثابتًا دائمًا",
  M4: "الجهد والتيار شيء واحد",
  M5: "المكوّن يستهلك التيار بالكامل",
  M6: "التيار يصل للمكونات واحدًا تلو الآخر",
  M7: "التيار يتوزع بالتساوي دائمًا في التوازي",
  M8: "إضافة مقاومة تقلل التيار في كل مكان بالتساوي",
  TM1: "المتغير المُسنَد يبقى مرتبطًا بمصدره",
  TM2: "أسطر البرنامج تُنفذ في الوقت نفسه",
  TM3: "الحلقة تشمل قيمة stop دائمًا",
  TM4: "شرط الحلقة يُفحص مرة واحدة فقط",
  TM5: "شروط SQL تُنفذ من اليسار إلى اليمين",
  TM6: "AND وOR يعملان بالطريقة نفسها",
  TM7: "Accuracy العالية تكفي للحكم على AI",
  TM8: "عدم توازن الفئات لا يؤثر على التقييم",
  EM1: "المساند تتقاسم الحمل بالتساوي دائمًا",
  EM2: "العضو الأكبر يحمل قوة أكبر دائمًا",
  EM3: "أقوى تصميم هو الأفضل تلقائيًا",
  EM4: "Criteria وConstraints لهما المعنى نفسه",
  EM5: "تغيير جزء يؤثر في هذا الجزء فقط",
  EM6: "التكرار يضاعف القدرة دائمًا",
  EM7: "أرخص تصميم هو التصميم الأمثل",
  EM8: "Optimization يعني تعظيم مؤشر واحد",
  MM1: "الحد يغير إشارته فقط لأنه انتقل",
  MM2: "العامل خارج القوس يوزع على الحد الأول فقط",
  MM3: "يمكن لمدخل واحد امتلاك عدة مخرجات",
  MM4: "اختبار الخط العمودي يفحص قيم y المتكررة",
  MM5: "إذا زادت كميتان فهما متناسبتان",
  MM6: "الفرق الثابت يثبت التناسب",
  MM7: "العبارة الشرطية وعكسها متكافئان",
  MM8: "مثال واحد يثبت قاعدة عامة",
};

const COPY = {
  en: {
    navHome: "Home",
    navLab: "Diagnostic Lab",
    navInsights: "Insights",
    navSystem: "System",
    heroEyebrow: "AI × COGNITIVE SCIENCE × STEM",
    heroTitleA: "See the",
    heroTitleB: "model behind",
    heroTitleC: "the mistake.",
    heroBody:
      "Misconception MRI infers the hidden mental model, teaches the exact missing idea, verifies the learner's new reasoning, and turns persistent patterns into a major-aware study plan.",
    start: "Start a live scan",
    explore: "Explore the system",
    live: "COGNITIVE DIAGNOSTICS PLATFORM",
    stack1: "32 misconception hypotheses",
    stack2: "Reasoning-based verification",
    stack3: "Major-aware study plans",
    stack4: "Deterministic STEM evidence",
    ordinary: "Ordinary AI",
    ordinaryBody: "Explains the correct answer after the student is wrong.",
    mri: "Misconception MRI",
    mriBody: "Finds the belief, repairs it with targeted learning, and verifies whether the reasoning actually changed.",
    problem: "The educational gap",
    problemBody:
      "Students can memorize a correct answer while keeping the wrong mental model. That hidden model causes the same error again in a new context.",
    how: "One closed learning loop",
    step1: "Predict",
    step1b: "Capture what the learner expects.",
    step2: "Diagnose",
    step2b: "Parse reasoning and update competing misconception hypotheses.",
    step3: "Challenge",
    step3b: "Choose the experiment with the highest expected information gain.",
    step4: "Verify & plan",
    step4b: "Re-evaluate reasoning; resolve the misconception or prioritize it in a major-aware study plan.",
    labTitle: "Diagnostic Lab",
    labSub: "Circuit 01 · identical bulbs in series",
    activeSession: "ACTIVE SESSION",
    engineOnline: "ENGINE ONLINE",
    predict: "Predict",
    diagnose: "Diagnose",
    challenge: "Challenge",
    update: "Update",
    question: "Which bulb will be brighter?",
    reason: "Explain why you think that.",
    reasonPlaceholder: "Describe what you think happens to the electricity...",
    scan: "Scan mental model",
    scanning: "Scanning reasoning...",
    scanTitle: "Mental model scan",
    neural: "COMPETING HYPOTHESES",
    parser: "Reasoning parser",
    detectedClaims: "Detected reasoning signals",
    generate: "Generate diagnostic experiment",
    activeLearning: "ACTIVE LEARNING SELECTION",
    selectedBy: "Selected by expected information gain",
    whyExperiment: "Why this experiment?",
    whyExperimentBody:
      "This counterexample is selected because the possible student beliefs predict different outcomes here. One observation can eliminate multiple explanations.",
    yourPrediction: "Your prediction",
    run: "Run experiment",
    running: "Running evidence engine...",
    evidence: "Evidence changed your model.",
    survived: "Prediction survived",
    conflict: "Prediction conflict detected",
    beforeEvidence: "Before evidence",
    afterEvidence: "After evidence",
    actualMeasurements: "Deterministic measurements",
    another: "Run another scan",
    quoteA: "We don't personalize the explanation.",
    quoteB: "We personalize the contradiction.",
    insightsTitle: "Learning Insights",
    insightsSub: "Learner diagnostic history and belief-shift analytics",
    totalScans: "Completed scans",
    avgShift: "Average belief shift",
    strongest: "Largest shift",
    recent: "Recent scans",
    noHistory: "Complete a diagnostic scan to build a learner history.",
    misconceptionMap: "Misconception map",
    misconceptionMapSub: "What this learner has shown across completed scans.",
    systemTitle: "Transparent AI architecture",
    systemSub:
      "The language model interprets reasoning. It does not calculate STEM results or decide truth.",
    llm: "GPT-OSS 120B",
    llmBody: "Extracts structured reasoning signals from the student's explanation.",
    bayes: "Bayesian learner model",
    bayesBody: "Maintains probabilities across competing misconception hypotheses.",
    info: "Information gain",
    infoBody: "Selects the next experiment that is expected to reduce uncertainty the most.",
    physics: "Evidence engines",
    physicsBody: "Compute observable results using deterministic physics, code, engineering, and mathematics.",
    separation: "AI / truth separation",
    separationBody:
      "The LLM reads language. The Bayesian model tracks beliefs. Deterministic STEM engines determine the experimental result. This keeps the system explainable and reproducible.",
    same: "Same brightness",
    bulbA: "Bulb A",
    bulbB: "Bulb B",
    currentModel: "Current model",
    confidence: "confidence",
    sessionHistory: "Session history",
    browserOnly: "Persistent learner history",
    scenarioLibrary: "Scenario library",
    scenarioLibrarySub: "Select a diagnostic environment",
    learnerProfile: "Learner profile",
    anonymousProfile: "Verified learner account",
    clearHistory: "Clear history",
    coverage: "Scenario coverage",
    persisted: "Server-side persistence",
  },
  ar: {
    navHome: "الرئيسية",
    navLab: "مختبر التشخيص",
    navInsights: "التحليلات",
    navSystem: "النظام",
    heroEyebrow: "ذكاء اصطناعي × علم الإدراك × STEM",
    heroTitleA: "اكتشف",
    heroTitleB: "النموذج الذهني",
    heroTitleC: "خلف الخطأ.",
    heroBody:
      "يستنتج Misconception MRI النموذج الذهني الخفي، ويعلّم الفكرة الناقصة تحديدًا، ويتحقق من reasoning الجديد، ثم يحوّل الأنماط المستمرة إلى خطة مبنية على تخصص الطالب.",
    start: "ابدأ فحصًا مباشرًا",
    explore: "استكشف النظام",
    live: "منصة تشخيص إدراكي",
    stack1: "32 فرضية للأفكار الخاطئة",
    stack2: "تحقق مبني على reasoning",
    stack3: "خطط حسب التخصص",
    stack4: "أدلة STEM حتمية",
    ordinary: "الذكاء الاصطناعي التقليدي",
    ordinaryBody: "يشرح الإجابة الصحيحة بعد أن يخطئ الطالب.",
    mri: "Misconception MRI",
    mriBody: "يكتشف الاعتقاد، ويعالجه بتعلم مستهدف، ثم يتحقق هل تغيّرت طريقة التفكير فعلًا.",
    problem: "الفجوة التعليمية",
    problemBody:
      "قد يحفظ الطالب الإجابة الصحيحة بينما يحتفظ بنموذج ذهني خاطئ، فيكرر الخطأ نفسه عندما يتغير السياق.",
    how: "حلقة تعلم مغلقة واحدة",
    step1: "توقّع",
    step1b: "نسجل ما يتوقعه الطالب.",
    step2: "شخّص",
    step2b: "نحلل تفسيره ونحدّث احتمالات الأفكار الخاطئة المتنافسة.",
    step3: "تحدّى",
    step3b: "نختار التجربة ذات أعلى مكسب معلومات متوقع.",
    step4: "تحقق وخطّط",
    step4b: "نعيد تقييم reasoning؛ نغلق الفكرة أو نعطيها أولوية في خطة مبنية على التخصص.",
    labTitle: "مختبر التشخيص",
    labSub: "الدائرة 01 · مصباحان متطابقان على التوالي",
    activeSession: "جلسة نشطة",
    engineOnline: "المحرك متصل",
    predict: "توقّع",
    diagnose: "شخّص",
    challenge: "تحدّى",
    update: "حدّث",
    question: "أي مصباح سيكون أكثر سطوعًا؟",
    reason: "اشرح لماذا تعتقد ذلك.",
    reasonPlaceholder: "اشرح ماذا تعتقد أنه يحدث للكهرباء...",
    scan: "افحص النموذج الذهني",
    scanning: "جاري تحليل التفكير...",
    scanTitle: "فحص النموذج الذهني",
    neural: "فرضيات متنافسة",
    parser: "محلل التفكير",
    detectedClaims: "إشارات التفكير المكتشفة",
    generate: "ولّد التجربة التشخيصية",
    activeLearning: "اختيار بالتعلم النشط",
    selectedBy: "تم الاختيار حسب مكسب المعلومات المتوقع",
    whyExperiment: "لماذا هذه التجربة؟",
    whyExperimentBody:
      "اختار النظام هذه التجربة لأن المعتقدات المحتملة تتوقع نتائج مختلفة فيها، لذلك يمكن لمشاهدة واحدة استبعاد عدة تفسيرات.",
    yourPrediction: "توقعك",
    run: "شغّل التجربة",
    running: "جاري تشغيل محرك الدليل...",
    evidence: "الدليل غيّر نموذجك.",
    survived: "التوقع صمد أمام الدليل",
    conflict: "تم اكتشاف تعارض بين التوقع والدليل",
    beforeEvidence: "قبل الدليل",
    afterEvidence: "بعد الدليل",
    actualMeasurements: "القياسات الحتمية",
    another: "ابدأ فحصًا جديدًا",
    quoteA: "نحن لا نخصص الشرح فقط.",
    quoteB: "نحن نخصص التناقض الذي يغيّر الفهم.",
    insightsTitle: "تحليلات التعلم",
    insightsSub: "سجل تشخيص المتعلم وتحليلات تغيّر المعتقد",
    totalScans: "الفحوص المكتملة",
    avgShift: "متوسط تغير الاعتقاد",
    strongest: "أكبر تغير",
    recent: "آخر الفحوص",
    noHistory: "أكمل فحصًا تشخيصيًا لبناء سجل تعلم.",
    misconceptionMap: "خريطة الأفكار الخاطئة",
    misconceptionMapSub: "ما أظهره هذا المتعلم عبر الجلسات المكتملة.",
    systemTitle: "بنية ذكاء اصطناعي شفافة",
    systemSub: "النموذج اللغوي يفسر reasoning فقط؛ لا يحسب نتائج STEM ولا يقرر الحقيقة.",
    llm: "GPT-OSS 120B",
    llmBody: "يستخرج إشارات تفكير منظمة من تفسير الطالب.",
    bayes: "نموذج بايزي للمتعلم",
    bayesBody: "يحافظ على احتمالات متعددة للأفكار الخاطئة المتنافسة.",
    info: "مكسب المعلومات",
    infoBody: "يختار التجربة التالية المتوقع أن تقلل عدم اليقين بأكبر قدر.",
    physics: "محركات الدليل",
    physicsBody: "تحسب النتائج باستخدام الفيزياء والكود والهندسة والرياضيات بصورة حتمية.",
    separation: "فصل الذكاء الاصطناعي عن الحقيقة",
    separationBody:
      "النموذج اللغوي يقرأ اللغة، والنموذج البايزي يتابع المعتقدات، ومحركات STEM تحدد نتيجة التجربة. لذلك يبقى النظام قابلًا للتفسير وإعادة الإنتاج.",
    same: "نفس السطوع",
    bulbA: "المصباح A",
    bulbB: "المصباح B",
    currentModel: "النموذج الحالي",
    confidence: "ثقة",
    sessionHistory: "سجل الجلسات",
    browserOnly: "سجل تعلم محفوظ بشكل مستمر",
    scenarioLibrary: "مكتبة السيناريوهات",
    scenarioLibrarySub: "اختر بيئة تشخيصية",
    learnerProfile: "ملف المتعلم",
    anonymousProfile: "حساب متعلم موثّق",
    clearHistory: "مسح السجل",
    coverage: "تغطية السيناريوهات",
    persisted: "حفظ على الخادم",
  },
};

export default function Home() {
  const [view, setView] = useState<View>("home");
  const [stage, setStage] = useState<Stage>("diagnose");
  const [lang, setLang] = useState<Lang>("en");
  const [answer, setAnswer] = useState<"A" | "B" | "same" | "">("");
  const [reasoning, setReasoning] = useState(
    "Because electricity reaches bulb A first, and A is closer to the battery."
  );
  const [diagnosis, setDiagnosis] = useState<Diagnosis | null>(null);
  const [prediction, setPrediction] = useState("");
  const [simulation, setSimulation] = useState<Simulation | null>(null);
  const [after, setAfter] = useState<Record<string, number> | null>(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<ScanRecord[]>([]);
  const [insights, setInsights] = useState<InsightsPayload>({ totalScans: 0, averageShift: 0, largestShift: 0, aggregated: [], scenarioCoverage: [], domainCoverage: [], interventionProgress: { completed: 0, resolved: 0, persistent: 0, resolutionRate: 0 } });
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState("S1");
  const [activeDomain, setActiveDomain] = useState<Scenario["domain"]>("science");
  const [auth, setAuth] = useState<AuthState>({ authenticated: false });
  const [platformStatus, setPlatformStatus] = useState<PlatformStatus | null>(null);

  const t = COPY[lang];
  const rtl = lang === "ar";
  const selectedScenario = scenarios.find((item) => item.id === selectedScenarioId) || scenarios[0] || null;
  const filteredScenarios = scenarios.filter((item) => item.domain === activeDomain);

  useEffect(() => {
    const savedLang = window.localStorage.getItem("mri_lang") as Lang | null;
    if (savedLang === "ar" || savedLang === "en") setLang(savedLang);

    Promise.all([
      fetch(`${API}/api/scenarios`).then((r) => r.ok ? r.json() : Promise.reject(new Error("scenarios"))),
      fetch(`${API}/api/status`).then((r) => r.ok ? r.json() : null),
      getAuthState(),
    ]).then(([scenarioData, statusData, authState]) => {
      setScenarios(scenarioData);
      setPlatformStatus(statusData);
      setAuth(authState);
      if (authState.authenticated) refreshLearnerData();
      const requestedView = new URLSearchParams(window.location.search).get("view");
      if (requestedView === "home") setView("home");
      if (requestedView === "system") setView("system");
      if (requestedView === "lab" || requestedView === "insights") {
        if (!authState.authenticated) {
          window.location.href = "/signin";
          return;
        }
        setView(requestedView);
        if (requestedView === "lab" && !diagnosis) setStage("diagnose");
      }
      const savedScenario = window.localStorage.getItem("mri_scenario_id");
      const requestedDomain = new URLSearchParams(window.location.search).get("domain");
      const validDomain = ["science", "technology", "engineering", "mathematics"].includes(requestedDomain || "")
        ? requestedDomain as Scenario["domain"]
        : null;
      const initial = scenarioData.find((item: Scenario) => item.id === savedScenario && (!validDomain || item.domain === validDomain))
        || scenarioData.find((item: Scenario) => item.domain === validDomain)
        || scenarioData[0];
      if (initial) {
        setActiveDomain(initial.domain);
        setSelectedScenarioId(initial.id);
        setReasoning((savedLang === "ar" ? initial.sample_reasoning_ar : initial.sample_reasoning) || "");
      }
    }).catch((error) => console.error("Platform bootstrap failed", error));

  }, []);

  useEffect(() => {
    if (!selectedScenario) return;
    if (stage === "diagnose" && !diagnosis) {
      setReasoning(lang === "ar" ? selectedScenario.sample_reasoning_ar : selectedScenario.sample_reasoning);
    }
  }, [lang]);

  async function refreshLearnerData() {
    try {
      const [historyRes, insightsRes] = await Promise.all([
        apiFetch(`/api/history?limit=50`),
        apiFetch(`/api/insights`),
      ]);
      if (historyRes.ok) {
        const payload = await historyRes.json();
        setHistory(payload.items || []);
      }
      if (insightsRes.ok) setInsights(await insightsRes.json());
    } catch (error) {
      console.error("Learner history unavailable", error);
    }
  }

  function toggleLanguage() {
    const next: Lang = lang === "en" ? "ar" : "en";
    setLang(next);
    window.localStorage.setItem("mri_lang", next);
    if (selectedScenario && stage === "diagnose") {
      setReasoning(next === "ar" ? selectedScenario.sample_reasoning_ar : selectedScenario.sample_reasoning);
    }
  }

  function selectScenario(id: string) {
    const scenario = scenarios.find((item) => item.id === id);
    if (!scenario) return;
    setSelectedScenarioId(id);
    setActiveDomain(scenario.domain);
    window.localStorage.setItem("mri_scenario_id", id);
    setStage("diagnose");
    setAnswer("");
    setDiagnosis(null);
    setPrediction("");
    setSimulation(null);
    setAfter(null);
    setReasoning(lang === "ar" ? scenario.sample_reasoning_ar : scenario.sample_reasoning);
  }

  const topBefore = diagnosis?.top_hypotheses?.[0];
  const topAfter = useMemo(() => {
    if (!after) return null;
    const entries = Object.entries(after) as [string, number][];
    const [id, probability] = entries.sort((a, b) => b[1] - a[1])[0];
    return { id, probability };
  }, [after]);

  const aggregated = insights.aggregated || [];

  function displayHypothesis(h: Hypothesis) {
    return lang === "ar" ? MISCONCEPTION_AR[h.id] || h.name : h.name;
  }

  async function diagnose() {
    if (!auth.authenticated || !auth.csrf_token) { window.location.href = "/signin"; return; }
    if (!answer || !reasoning.trim() || !selectedScenario) return;
    setLoading(true);
    try {
      const res = await apiFetch(`/api/diagnose`, {
        method: "POST",
        headers: { "X-CSRF-Token": auth.csrf_token },
        body: JSON.stringify({ answer, reasoning, scenario_id: selectedScenario.id }),
      });
      if (!res.ok) throw new Error(`Diagnosis failed: ${res.status}`);
      const data: Diagnosis = await res.json();
      setDiagnosis(data);
      setAfter(null);
      setPrediction("");
      setSimulation(null);
      setStage("scan");
    } catch (error) {
      console.error(error);
      alert(lang === "ar" ? "خدمة التشخيص غير متاحة مؤقتًا. حاول مرة أخرى." : "Diagnostic service is temporarily unavailable. Please retry.");
    } finally {
      setLoading(false);
    }
  }

  async function runExperiment() {
    if (!diagnosis || !prediction) return;
    setLoading(true);
    try {
      const simRes = await fetch(`${API}/api/simulate/${diagnosis.next_experiment.id}`);
      if (!simRes.ok) throw new Error(`Simulation failed: ${simRes.status}`);
      const simData: Simulation = await simRes.json();
      setSimulation(simData);

      const updateRes = await apiFetch(`/api/update`, {
        method: "POST",
        headers: { "X-CSRF-Token": auth.csrf_token || "" },
        body: JSON.stringify({
          experiment_id: diagnosis.next_experiment.id,
          outcome: simData.actual_outcome,
          prior: diagnosis.posterior,
          scan_id: diagnosis.scan_id || undefined,
        }),
      });
      if (!updateRes.ok) throw new Error(`Model update failed: ${updateRes.status}`);
      const up: { posterior: Record<string, number> } = await updateRes.json();
      setAfter(up.posterior);
      setStage("result");
      await refreshLearnerData();
    } catch (error) {
      console.error(error);
      alert(lang === "ar" ? "خدمة التجربة غير متاحة مؤقتًا. حاول مرة أخرى." : "Experiment service is temporarily unavailable. Please retry.");
    } finally {
      setLoading(false);
    }
  }

  async function clearLearnerHistory() {
    if (!auth.authenticated || !auth.csrf_token) return;
    const ok = window.confirm(lang === "ar" ? "هل تريد مسح سجل التعلم من حسابك؟" : "Clear diagnostic history from your account?");
    if (!ok) return;
    try {
      await apiFetch(`/api/history`, { method: "DELETE", headers: { "X-CSRF-Token": auth.csrf_token } });
      await refreshLearnerData();
    } catch (error) {
      console.error(error);
    }
  }

  function reset() {
    setStage("diagnose");
    setAnswer("");
    setDiagnosis(null);
    setPrediction("");
    setSimulation(null);
    setAfter(null);
    if (selectedScenario) setReasoning(lang === "ar" ? selectedScenario.sample_reasoning_ar : selectedScenario.sample_reasoning);
  }

  function openLab() {
    if (!auth.authenticated) { window.location.href = "/signin"; return; }
    setView("lab");
    if (!diagnosis) setStage("diagnose");
  }

  function openInsights() {
    if (!auth.authenticated) { window.location.href = "/signin"; return; }
    setView("insights");
  }

  return (
    <main className="site" dir={rtl ? "rtl" : "ltr"}>
      <Navbar
        activeView={view}
        labels={t}
        auth={auth}
        lang={lang}
        platformStatus={platformStatus?.status}
        onHome={() => setView("home")}
        onLab={openLab}
        onStem={() => { window.location.href = "/stem"; }}
        onInsights={openInsights}
        onSystem={() => setView("system")}
        onToggleLanguage={toggleLanguage}
      />

      {view === "home" && (
        <div className="home-page">
          <section className="hero-v3">
            <div className="hero-copy-v3">
              <div className="eyebrow-row">
                <span className="live-pill"><Radio size={14} strokeWidth={2} /><i /> {t.live}</span>
                <span>{t.heroEyebrow}</span>
              </div>
              <h1>{t.heroTitleA} <em>{t.heroTitleB}</em> {t.heroTitleC}</h1>
              <p>{t.heroBody}</p>
              <div className="hero-actions">
                <button className="btn-primary" onClick={openLab}>{t.start}<ArrowRight size={17} strokeWidth={2.2} /></button>
                <button className="btn-ghost" onClick={() => setView("system")}><Network size={16} strokeWidth={1.9} />{t.explore}</button>
              </div>
              <div className="hero-proof-grid">
                <div className="proof-card">
                  <span className="proof-index"><BrainCircuit size={16} strokeWidth={1.9} /></span>
                  <div><b>GPT-OSS 120B</b><small>{lang === "ar" ? "استخراج إشارات التفكير" : "Reasoning extraction"}</small></div>
                  <i>LIVE</i>
                </div>
                <div className="proof-card">
                  <span className="proof-index"><Activity size={16} strokeWidth={1.9} /></span>
                  <div><b>{lang === "ar" ? "تشخيص بايزي" : "Bayesian Diagnosis"}</b><small>{lang === "ar" ? "فرضيات قابلة للتحديث" : "Updatable belief hypotheses"}</small></div>
                  <i>32 MODELS</i>
                </div>
                <div className="proof-card">
                  <span className="proof-index"><CircuitBoard size={16} strokeWidth={1.9} /></span>
                  <div><b>{lang === "ar" ? "محركات STEM حتمية" : "STEM Evidence Engines"}</b><small>{lang === "ar" ? "الدليل لا يأتي من الـLLM" : "Evidence never comes from the LLM"}</small></div>
                  <i>VERIFIED</i>
                </div>
              </div>
            </div>

            <div className="hero-intelligence-card">
              <div className="intelligence-topbar">
                <div>
                  <span className="console-dot" />
                  <span>{lang === "ar" ? "فحص إدراكي مباشر" : "LIVE COGNITIVE SCAN"}</span>
                </div>
                <b>student_01 · circuit_01</b>
              </div>

              <div className="cognitive-stage">
                <div className="cognitive-grid" />
                <div className="cognitive-scan-beam" />
                <svg className="mind-links" viewBox="0 0 600 390" preserveAspectRatio="none" aria-hidden="true">
                  <line x1="300" y1="190" x2="108" y2="96" />
                  <line x1="300" y1="190" x2="490" y2="86" />
                  <line x1="300" y1="190" x2="500" y2="286" />
                  <line x1="300" y1="190" x2="112" y2="292" />
                </svg>

                <div className="mind-core">
                  <span>MRI CORE</span>
                  <strong>{lang === "ar" ? "النموذج الذهني" : "MENTAL MODEL"}</strong>
                  <small>posterior state</small>
                  <div className="core-pulse" />
                </div>

                <div className="mind-node mind-node-a">
                  <span>M2</span>
                  <div>
                    <b>{lang === "ar" ? "الأقرب = قدرة أكبر" : "Closer = more power"}</b>
                    <small>{lang === "ar" ? "الفرضية الأقوى" : "dominant hypothesis"}</small>
                  </div>
                  <strong>64%</strong>
                </div>

                <div className="mind-node mind-node-b">
                  <span>M6</span>
                  <div>
                    <b>{lang === "ar" ? "وصول متتابع" : "Sequential arrival"}</b>
                    <small>secondary signal</small>
                  </div>
                  <strong>18%</strong>
                </div>

                <div className="mind-node mind-node-c">
                  <span>M1</span>
                  <div>
                    <b>{lang === "ar" ? "استهلاك التيار" : "Current consumed"}</b>
                    <small>weak signal</small>
                  </div>
                  <strong>11%</strong>
                </div>

                <div className="reasoning-signal">
                  <div className="signal-head">
                    <span>GPT-OSS 120B</span>
                    <b>{lang === "ar" ? "تحليل التفكير" : "REASONING SIGNAL"}</b>
                  </div>
                  <div className="signal-wave">
                    <i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i />
                  </div>
                  <p>{lang === "ar"
                    ? "«المصباح A أكثر سطوعًا لأن الكهرباء تصل إليه أولًا.»"
                    : "“Bulb A is brighter because electricity reaches it first.”"}</p>
                </div>
              </div>

              <div className="hero-decision-row">
                <div className="decision-chip">
                  <span>{lang === "ar" ? "التجربة التالية" : "NEXT BEST EXPERIMENT"}</span>
                  <b>{lang === "ar" ? "بدّل موضعي المصباحين" : "Swap identical bulbs"}</b>
                </div>
                <div className="information-chip">
                  <span>INFORMATION GAIN</span>
                  <strong>0.68 <small>bits</small></strong>
                </div>
              </div>

              <div className="evidence-preview">
                <span>{lang === "ar" ? "تحول الاعتقاد بعد الدليل" : "EVIDENCE SHIFT PREVIEW"}</span>
                <div><b>64%</b><i>→</i><strong>16%</strong></div>
              </div>
            </div>
          </section>

          <section className="comparison-section">
            <div className="section-heading">
              <span>{t.problem}</span>
              <h2>{t.problemBody}</h2>
            </div>
            <div className="comparison-grid">
              <article className="comparison-card ordinary-card">
                <span className="card-number">01</span>
                <h3>{t.ordinary}</h3>
                <p>{t.ordinaryBody}</p>
                <div className="chat-example">
                  <span><Cpu size={16} strokeWidth={1.8} /></span>
                  <p>“The correct answer is that both bulbs have the same brightness because...”</p>
                </div>
              </article>
              <article className="comparison-card mri-card">
                <span className="card-number">02</span>
                <h3>{t.mri}</h3>
                <p>{t.mriBody}</p>
                <div className="model-example">
                  <span>M2</span>
                  <div><b>Proximity model</b><small>64% → evidence challenge</small></div>
                  <strong><TrendingDown size={20} strokeWidth={2} /></strong>
                </div>
              </article>
            </div>
          </section>

          <section className="workflow-section">
            <div className="section-heading compact-heading">
              <span>{t.how}</span>
              <h2>Diagnose → Intervene → Practice → Verify → Plan</h2>
            </div>
            <div className="workflow-grid">
              <WorkflowCard n="01" title={t.step1} body={t.step1b} />
              <WorkflowCard n="02" title={t.step2} body={t.step2b} />
              <WorkflowCard n="03" title={t.step3} body={t.step3b} />
              <WorkflowCard n="04" title={t.step4} body={t.step4b} />
            </div>
          </section>
        </div>
      )}

      {view === "lab" && (
        <div className="product-layout">
          <aside className="product-sidebar">
            <div className="side-section-label">{t.scenarioLibrary}</div>
            <div className="domain-switcher">
              {(["science", "technology", "engineering", "mathematics"] as const).map((domain) => (
                <button
                  key={domain}
                  className={activeDomain === domain ? "active" : ""}
                  onClick={() => {
                    setActiveDomain(domain);
                    const first = scenarios.find((item) => item.domain === domain);
                    if (first) selectScenario(first.id);
                  }}
                >{domain === "science" ? "S" : domain === "technology" ? "T" : domain === "engineering" ? "E" : "M"}</button>
              ))}
            </div>
            <div className="scenario-stack">
              {filteredScenarios.map((item) => (
                <button key={item.id} className={`scenario-select ${item.id === selectedScenarioId ? "active" : ""}`} onClick={() => selectScenario(item.id)}>
                  <span><CircuitBoard size={16} strokeWidth={1.9} /></span>
                  <div><b>{item.code}</b><small>{lang === "ar" ? item.title_ar : item.title}</small></div>
                </button>
              ))}
            </div>
            <Link className="learner-card" href="/account">
              <span><UserRound size={16} strokeWidth={1.9} /></span>
              <div><b>{auth.user?.full_name || t.learnerProfile}</b><small>{auth.user?.email || "Account required"}</small></div>
              <i><Database size={14} strokeWidth={1.8} /></i>
            </Link>
            <div className="side-nav-stack">
              <button className="active"><span><ScanSearch size={15} strokeWidth={1.9} /></span>{t.labTitle}</button>
              <button onClick={openInsights}><span><ChartNoAxesCombined size={15} strokeWidth={1.9} /></span>{t.navInsights}</button>
              <button onClick={() => setView("system")}><span><Network size={15} strokeWidth={1.9} /></span>{t.navSystem}</button>
            </div>
            <div className="sidebar-engine">
              <span><i /> {t.engineOnline}</span>
              <b>Cloudflare Workers AI</b>
              <small>GPT-OSS 120B</small>
            </div>
          </aside>

          <section className="lab-main">
            <div className="lab-topline">
              <div>
                <span className="section-kicker">{t.labTitle}</span>
                <h1>{selectedScenario ? (lang === "ar" ? selectedScenario.title_ar : selectedScenario.title) : t.labSub}</h1>
              </div>
              <div className="stage-track">
                {[
                  { key: "predict", n: "01", label: t.predict, stages: ["diagnose"] },
                  { key: "diagnose", n: "02", label: t.diagnose, stages: ["scan"] },
                  { key: "challenge", n: "03", label: t.challenge, stages: ["experiment", "result"] },
                  { key: "intervene", n: "04", label: lang === "ar" ? "تدخل" : "Intervene", stages: ["intervention"] },
                  { key: "verify", n: "05", label: lang === "ar" ? "تحقق" : "Verify", stages: ["verification", "plan"] },
                ].map((item, index, items) => {
                  const current = items.findIndex((candidate) => candidate.stages.includes(stage));
                  return <div key={item.key} className={`${current === index ? "current" : ""} ${current > index ? "complete" : ""}`}><span>{item.n}</span><b>{item.label}</b></div>;
                })}
              </div>
            </div>

            <div className="lab-grid">
              <div className="experiment-canvas">
                <div className="canvas-header">
                  <div><span>{selectedScenario?.domain.toUpperCase()} ENVIRONMENT</span><b>{selectedScenario ? selectedScenario.code : "STEM LAB"}</b></div>
                  <div className="canvas-badges"><span>{selectedScenario?.topic || "STEM"}</span>{selectedScenario?.circuit.resistances.map((r, i) => <span key={i}>{r}Ω</span>)}</div>
                </div>
                <Circuit
                  variant={selectedScenario?.circuit.type || "series_bulbs"}
                  swapped={stage === "experiment" || stage === "result"}
                  running={stage === "result"}
                  scanning={loading && stage === "diagnose"}
                />

                {stage === "scan" && diagnosis && (
                  <div className="graph-panel">
                    <div className="graph-panel-title"><span>{t.currentModel}</span><b>{Math.round(diagnosis.top_hypotheses[0].probability * 100)}% {t.confidence}</b></div>
                    <ModelGraph hypotheses={diagnosis.top_hypotheses.map((h) => ({ ...h, name: displayHypothesis(h) }))} lang={lang} />
                  </div>
                )}

                {stage === "result" && simulation && (
                  <div className="measurement-grid-v3">
                    {Object.entries(simulation.measurements).map(([k, v]) => (
                      <div key={k} className="measurement-card-v3">
                        <span>{measurementLabel(k, lang)}</span>
                        <strong>{v}</strong>
                        <small>{measurementUnit(k)}</small>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="decision-panel">
                {stage === "diagnose" && (
                  <>
                    <PanelHeader n="01" kicker={t.predict} title={selectedScenario ? (lang === "ar" ? selectedScenario.question_ar : selectedScenario.question) : t.question} />
                    <div className="answer-cards">
                      {(selectedScenario?.options || []).map((opt) => (
                        <button key={opt.value} onClick={() => setAnswer(opt.value)} className={answer === opt.value ? "selected" : ""}>
                          <span>{opt.value === "same" ? "=" : opt.value}</span>
                          <b>{lang === "ar" ? opt.label_ar : opt.label}</b>
                        </button>
                      ))}
                    </div>
                    <label className="field-label">{t.reason}</label>
                    <textarea
                      className="reasoning-box"
                      placeholder={t.reasonPlaceholder}
                      value={reasoning}
                      onChange={(e) => setReasoning(e.target.value)}
                    />
                    <div className="input-meta"><span>Natural language reasoning</span><span>{reasoning.length}/1200</span></div>
                    <button className="action-button" disabled={!answer || loading} onClick={diagnose}>{loading ? t.scanning : t.scan}<ScanSearch size={18} strokeWidth={2} /></button>
                  </>
                )}

                {stage === "scan" && diagnosis && (
                  <>
                    <PanelHeader n="02" kicker={t.diagnose} title={t.scanTitle} />
                    <div className="signal-badge"><i /> {t.neural}</div>
                    <div className="belief-list-v3">
                      {diagnosis.top_hypotheses.map((h, index) => (
                        <div className="belief-row-v3" key={h.id}>
                          <div className="belief-rank">0{index + 1}</div>
                          <div className="belief-main">
                            <div><span>{displayHypothesis(h)}</span><b>{Math.round(h.probability * 100)}%</b></div>
                            <div className="belief-track"><i style={{ width: `${Math.max(4, h.probability * 100)}%` }} /></div>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="reasoning-card-v3">
                      <div className="reasoning-card-top"><span>{t.parser}</span><b>GPT-OSS 120B</b></div>
                      <p>“{diagnosis.parsed_reasoning.summary}”</p>
                      <div className="claim-chips">
                        {(diagnosis.parsed_reasoning.claims.length ? diagnosis.parsed_reasoning.claims : ["structured_reasoning"]).map((claim) => <span key={claim}>{claim.replaceAll("_", " ")}</span>)}
                      </div>
                    </div>
                    <button className="action-button" onClick={() => setStage("experiment")}>{t.generate}<ArrowRight size={18} strokeWidth={2.1} /></button>
                  </>
                )}

                {stage === "experiment" && diagnosis && (
                  <>
                    <PanelHeader n="03" kicker={t.challenge} title={diagnosis.next_experiment.name} />
                    <div className="ig-hero-card">
                      <div><span>{t.selectedBy}</span><strong>{diagnosis.next_experiment.information_gain.toFixed(2)}</strong></div>
                      <b>BITS</b>
                    </div>
                    <p className="panel-muted">{diagnosis.next_experiment.description}</p>
                    <div className="why-card"><span><Sparkles size={17} strokeWidth={1.9} /></span><div><b>{t.whyExperiment}</b><p>{t.whyExperimentBody}</p></div></div>
                    <div className="challenge-prompt">{diagnosis.next_experiment.prompt}</div>
                    <label className="field-label">{t.yourPrediction}</label>
                    <div className="prediction-stack">
                      {diagnosis.next_experiment.options.map((opt) => (
                        <button key={opt} onClick={() => setPrediction(opt)} className={prediction === opt ? "selected" : ""}>{pretty(opt, lang)}<span>{prediction === opt ? <Check size={16} strokeWidth={2.3} /> : <ChevronRight size={16} strokeWidth={2} />}</span></button>
                      ))}
                    </div>
                    <button className="action-button danger-button" disabled={!prediction || loading} onClick={runExperiment}>{loading ? t.running : t.run}<Play size={18} fill="currentColor" strokeWidth={1.8} /></button>
                  </>
                )}

                {stage === "result" && diagnosis && simulation && (
                  <>
                    <PanelHeader n="04" kicker={t.update} title={t.evidence} />
                    <div className={`conflict-v3 ${prediction === simulation.actual_outcome ? "resolved" : "detected"}`}>
                      <span>{prediction === simulation.actual_outcome ? <BadgeCheck size={20} strokeWidth={2} /> : <Zap size={20} strokeWidth={2} />}</span>
                      <div><b>{prediction === simulation.actual_outcome ? t.survived : t.conflict}</b><small>{t.actualMeasurements}</small></div>
                    </div>

                    {topBefore && (
                      <div className="shift-visual">
                        <div><span>{t.beforeEvidence}</span><strong>{Math.round(topBefore.probability * 100)}%</strong></div>
                        <div className="shift-arrow"><i /><ArrowRight size={19} strokeWidth={2} /><i /></div>
                        <div><span>{t.afterEvidence}</span><strong>{Math.round((after?.[topBefore.id] || 0) * 100)}%</strong></div>
                        <p>{displayHypothesis(topBefore)}</p>
                      </div>
                    )}

                    <div className="evidence-explanation"><span>EVIDENCE</span><p>{simulation.explanation}</p></div>
                    <blockquote><span>“{t.quoteA}</span> <b>{t.quoteB}”</b></blockquote>
                    <div className="result-actions">
                      <button className="action-button" onClick={() => setStage("intervention")}>{lang === "ar" ? "ابدأ التدخل المستهدف" : "Start targeted intervention"}<ArrowRight size={17} strokeWidth={2} /></button>
                      <button className="outline-button" onClick={reset}>{t.another}</button>
                      <button className="outline-button" onClick={openInsights}>{t.navInsights}</button>
                    </div>
                  </>
                )}

                {(["intervention", "verification", "plan"] as Stage[]).includes(stage) && diagnosis?.scan_id && (
                  <InterventionFlow
                    scanId={diagnosis.scan_id}
                    csrfToken={auth.csrf_token || ""}
                    lang={lang}
                    initialMajor={auth.user?.academic_major || "undecided"}
                    misconceptionLabel={topBefore ? displayHypothesis(topBefore) : ""}
                    onPhaseChange={(next) => setStage(next)}
                    onReset={reset}
                    onInsights={openInsights}
                  />
                )}
              </div>
            </div>
          </section>
        </div>
      )}

      {view === "insights" && (
        <div className="dashboard-page">
          <div className="dashboard-heading">
            <div><span className="section-kicker">{t.navInsights}</span><h1>{t.insightsTitle}</h1><p>{t.insightsSub}</p></div>
            <div className="dashboard-actions"><button className="outline-button small-btn" onClick={clearLearnerHistory}><Trash2 size={15} strokeWidth={1.9} />{t.clearHistory}</button><button className="btn-primary small-btn" onClick={openLab}>{t.start}<ArrowRight size={16} strokeWidth={2} /></button></div>
          </div>
          <div className="metric-grid">
            <MetricCard label={t.totalScans} value={`${insights.totalScans}`} note={t.persisted} />
            <MetricCard label={t.avgShift} value={`${Math.round(insights.averageShift * 100)}%`} note="Bayesian posterior change" />
            <MetricCard label={t.strongest} value={`${Math.round(insights.largestShift * 100)}%`} note="Single diagnostic counterexample" />
            <MetricCard label="STEM domains" value={`${insights.domainCoverage?.length || 0}/4`} note="Science · Technology · Engineering · Math" />
            <MetricCard label={lang === "ar" ? "الأفكار التي تم حلها" : "Misconceptions resolved"} value={`${insights.interventionProgress?.resolved || 0}/${insights.interventionProgress?.completed || 0}`} note={lang === "ar" ? "تم التحقق من reasoning" : "Reasoning-verified interventions"} />
          </div>

          <div className="insights-grid">
            <section className="insight-card large-card">
              <div className="card-heading"><div><span>{t.misconceptionMap}</span><p>{t.misconceptionMapSub}</p></div><b>LIVE</b></div>
              {aggregated.length ? (
                <ModelGraph hypotheses={aggregated.map((h) => ({ ...h, name: lang === "ar" ? MISCONCEPTION_AR[h.id] || h.name : h.name }))} lang={lang} />
              ) : (
                <div className="empty-state"><span><BrainCircuit size={38} strokeWidth={1.5} /></span><p>{t.noHistory}</p></div>
              )}
            </section>

            <section className="insight-card history-card">
              <div className="card-heading"><div><span>{t.recent}</span><p>{t.sessionHistory}</p></div><b>{history.length}</b></div>
              <div className="history-list">
                {history.length ? history.slice(0, 6).map((item) => (
                  <div className="history-row" key={item.id}>
                    <div className="history-icon"><BrainCircuit size={16} strokeWidth={1.8} /></div>
                    <div className="history-copy"><b>{lang === "ar" ? MISCONCEPTION_AR[item.misconceptionId] || item.misconception : item.misconception}</b><span>{new Date(item.createdAt).toLocaleString(lang === "ar" ? "ar-JO" : "en-GB")}</span></div>
                    <div className="history-shift"><span>{Math.round(item.before * 100)}%</span><i><ArrowRight size={13} strokeWidth={2} /></i><b>{Math.round((item.after || 0) * 100)}%</b></div>
                  </div>
                )) : <div className="empty-list">{t.noHistory}</div>}
              </div>
            </section>
          </div>
          <section className="coverage-card">
            <div className="card-heading"><div><span>{t.coverage}</span><p>{t.scenarioLibrarySub}</p></div><b>{insights.scenarioCoverage.length}</b></div>
            <div className="coverage-grid">
              {insights.scenarioCoverage.length ? insights.scenarioCoverage.map((item) => (
                <div key={item.id} className="coverage-item"><Layers3 size={16} strokeWidth={1.8} /><div><b>{item.title}</b><span>{item.count} {lang === "ar" ? "فحص" : "scans"}</span></div></div>
              )) : <div className="empty-list">{t.noHistory}</div>}
            </div>
          </section>
        </div>
      )}

      {view === "system" && (
        <div className="system-page">
          <div className="system-hero">
            <span className="section-kicker">AI ARCHITECTURE</span>
            <h1>{t.systemTitle}</h1>
            <p>{t.systemSub}</p>
          </div>

          <div className="platform-facts">
            <div className="platform-fact"><span>Platform status</span><b>{platformStatus?.status || "unknown"}</b></div>
            <div className="platform-fact"><span>Persistence</span><b>{platformStatus?.persistence || "postgresql"}</b></div>
            <div className="platform-fact"><span>Diagnostic scenarios</span><b>{platformStatus?.scenario_count ?? scenarios.length}</b></div>
            <div className="platform-fact"><span>Evidence engines</span><b>{platformStatus?.evidence_engines?.length || 4} deterministic</b></div>
          </div>

          <div className="architecture-flow">
            <ArchitectureNode code="01" title={t.llm} body={t.llmBody} badge="LANGUAGE" />
            <div className="flow-arrow"><ArrowRight size={20} strokeWidth={1.8} /></div>
            <ArchitectureNode code="02" title={t.bayes} body={t.bayesBody} badge="INFERENCE" />
            <div className="flow-arrow"><ArrowRight size={20} strokeWidth={1.8} /></div>
            <ArchitectureNode code="03" title={t.info} body={t.infoBody} badge="SELECTION" />
            <div className="flow-arrow"><ArrowRight size={20} strokeWidth={1.8} /></div>
            <ArchitectureNode code="04" title={t.physics} body={t.physicsBody} badge="TRUTH" />
          </div>

          <section className="separation-card">
            <div className="separation-visual">
              <div className="ring ring-a"><span>AI</span></div>
              <div className="ring ring-b"><span>BAYES</span></div>
              <div className="ring ring-c"><span>EVIDENCE</span></div>
            </div>
            <div><span>{t.separation}</span><h2>Language ≠ belief ≠ evidence</h2><p>{t.separationBody}</p></div>
          </section>

          <div className="system-feature-grid">
            <SystemFeature title="Structured reasoning" body="The model returns a constrained set of misconception labels instead of free-form tutoring." icon="brain" />
            <SystemFeature title="Resilient inference path" body="If the external inference provider is unavailable, the service degrades gracefully to a transparent heuristic parser." icon="cloud" />
            <SystemFeature title="Reproducible STEM evidence" body="Physics, code traces, engineering equations, and mathematics are computed by deterministic engines—not invented by an LLM." icon="check" />
            <SystemFeature title="Account-scoped learner history" body="Learner scans are stored in PostgreSQL under the authenticated account, so progress follows the learner across devices and future STEM domains." icon="shield" />
          </div>
        </div>
      )}
    </main>
  );
}

function BeliefMini({ label, value }: { label: string; value: number }) {
  return <div className="belief-mini"><div><span>{label}</span><b>{value}%</b></div><div className="mini-track"><i style={{ width: `${value}%` }} /></div></div>;
}

function WorkflowCard({ n, title, body }: { n: string; title: string; body: string }) {
  return <article className="workflow-card"><span>{n}</span><h3>{title}</h3><p>{body}</p></article>;
}

function PanelHeader({ n, kicker, title }: { n: string; kicker: string; title: string }) {
  return <div className="panel-header-v3"><div><span>STEP {n} · {kicker}</span><h2>{title}</h2></div><b>{n}</b></div>;
}

function MetricCard({ label, value, note }: { label: string; value: string; note: string }) {
  return <article className="metric-card"><span>{label}</span><strong>{value}</strong><small>{note}</small></article>;
}

function ArchitectureNode({ code, title, body, badge }: { code: string; title: string; body: string; badge: string }) {
  return <article className="architecture-node"><div><span>{code}</span><b>{badge}</b></div><h3>{title}</h3><p>{body}</p></article>;
}

function SystemFeature({ title, body, icon = "check" }: { title: string; body: string; icon?: "check" | "brain" | "cloud" | "shield" }) {
  const Icon = icon === "brain" ? BrainCircuit : icon === "cloud" ? CloudCog : icon === "shield" ? ShieldCheck : BadgeCheck;
  return <article className="system-feature"><span><Icon size={17} strokeWidth={1.9} /></span><div><b>{title}</b><p>{body}</p></div></article>;
}

function pretty(value: string, lang: Lang) {
  const en: Record<string, string> = {
    A: "Bulb A",
    B: "Bulb B",
    same: "Same",
    first_higher: "First is higher",
    second_higher: "Second is higher",
    decreases: "Decreases",
    increases: "Increases",
    equal: "Equal",
    lower_resistance_more: "Lower resistance → more current",
    higher_resistance_more: "Higher resistance → more current",
  };
  const ar: Record<string, string> = {
    A: "المصباح A",
    B: "المصباح B",
    same: "متساويان",
    first_higher: "الأول أعلى",
    second_higher: "الثاني أعلى",
    decreases: "ينخفض",
    increases: "يزداد",
    equal: "متساوي",
    lower_resistance_more: "المقاومة الأقل → تيار أكبر",
    higher_resistance_more: "المقاومة الأعلى → تيار أكبر",
  };
  const map = lang === "ar" ? ar : en;
  return map[value] || value.replaceAll("_", " ");
}

function measurementLabel(value: string, lang: Lang) {
  if (lang === "en") return value.replaceAll("_", " ");
  const map: Record<string, string> = {
    current_A: "تيار A",
    current_B: "تيار B",
    power_A: "قدرة A",
    power_B: "قدرة B",
    current_before: "التيار قبل",
    current_after: "التيار بعد",
    branch_15_ohm: "فرع 15Ω",
    branch_30_ohm: "فرع 30Ω",
  };
  return map[value] || value.replaceAll("_", " ");
}

function measurementUnit(key: string) {
  if (key.includes("percent")) return "%";
  if (key.includes("reaction")) return "kN";
  if (key.includes("stress")) return "MPa";
  if (key.includes("power")) return "W";
  if (key.includes("current") || key.includes("branch_")) return "A";
  return "";
}

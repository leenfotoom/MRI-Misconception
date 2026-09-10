"use client";

import { useEffect, useRef, useState } from "react";
import {
  ArrowRight,
  BadgeCheck,
  BookOpenCheck,
  BrainCircuit,
  Check,
  CircleAlert,
  ListChecks,
  RefreshCw,
  Route,
  Sparkles,
  Target,
} from "lucide-react";
import { apiFetch, authMutation } from "@/lib/api";

type Lang = "en" | "ar";

type Option = { value: "A" | "B" | "same"; label: string; label_ar: string };

type Intervention = {
  scan_id: string;
  misconception: { id: string; name: string; description: string; probability: number };
  simple_explanation: string;
  simple_explanation_ar: string;
  correct_model: string;
  correct_model_ar: string;
  micro_lesson: string[];
  micro_lesson_ar: string[];
  practice: { question: string; question_ar: string; options: Option[] };
};

type Verification = {
  status: "resolved" | "persistent";
  answer_correct: boolean;
  reasoning_matches_correct_model: boolean;
  same_misconception_detected: boolean;
  post_misconception_probability: number;
  feedback: string;
  feedback_ar: string;
};

type Major = { id: string; label: string; label_ar: string };

type Plan = {
  major: string;
  major_label: string;
  status: "action_required" | "on_track";
  summary: string;
  items: {
    id: string;
    sequence: number;
    domain: string;
    topic: string;
    focus: string;
    priority: "high" | "medium" | "low";
    severity_score: number;
    persistent_attempts: number;
    why: string;
    activities: string[];
    reassessment: string;
    progress_status: string;
  }[];
  progress: {
    interventions_completed: number;
    resolved: number;
    persistent: number;
    resolution_rate: number;
  };
  tracking_rule: string;
};

type Props = {
  scanId: string;
  csrfToken: string;
  lang: Lang;
  initialMajor: string;
  misconceptionLabel: string;
  onReset: () => void;
  onInsights: () => void;
  onPhaseChange: (phase: "intervention" | "verification" | "plan") => void;
};

export default function InterventionFlow({
  scanId,
  csrfToken,
  lang,
  initialMajor,
  misconceptionLabel,
  onReset,
  onInsights,
  onPhaseChange,
}: Props) {
  const [phase, setPhase] = useState<"learn" | "practice" | "verification" | "plan">("learn");
  const [intervention, setIntervention] = useState<Intervention | null>(null);
  const [verification, setVerification] = useState<Verification | null>(null);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [majors, setMajors] = useState<Major[]>([]);
  const [major, setMajor] = useState(initialMajor === "undecided" ? "" : initialMajor);
  const [answer, setAnswer] = useState<"A" | "B" | "same" | "">("");
  const [reasoning, setReasoning] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const started = useRef(false);
  const ar = lang === "ar";

  function move(next: "learn" | "practice" | "verification" | "plan") {
    setPhase(next);
    onPhaseChange(next === "verification" ? "verification" : next === "plan" ? "plan" : "intervention");
  }

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    Promise.all([
      apiFetch("/api/interventions/start", {
        method: "POST",
        headers: { "X-CSRF-Token": csrfToken },
        body: JSON.stringify({ scan_id: scanId }),
      }),
      apiFetch("/api/majors"),
    ])
      .then(async ([interventionRes, majorsRes]) => {
        if (!interventionRes.ok) throw new Error(`Intervention failed: ${interventionRes.status}`);
        setIntervention(await interventionRes.json());
        if (majorsRes.ok) setMajors(await majorsRes.json());
      })
      .catch(() => setError(ar ? "تعذر بدء التدخل المستهدف. أعد المحاولة." : "Could not start the targeted intervention. Please retry."))
      .finally(() => setLoading(false));
  }, [ar, csrfToken, scanId]);

  async function verify() {
    if (!answer || reasoning.trim().length < 5) return;
    setLoading(true);
    setError("");
    try {
      const res = await apiFetch("/api/interventions/verify", {
        method: "POST",
        headers: { "X-CSRF-Token": csrfToken },
        body: JSON.stringify({ scan_id: scanId, answer, reasoning }),
      });
      if (!res.ok) throw new Error(`Verification failed: ${res.status}`);
      setVerification(await res.json());
      move("verification");
    } catch {
      setError(ar ? "تعذر التحقق من الإجابة. حاول مرة أخرى." : "Could not verify the new reasoning. Please retry.");
    } finally {
      setLoading(false);
    }
  }

  async function generatePlan() {
    if (!major) return;
    setLoading(true);
    setError("");
    try {
      if (major !== initialMajor) {
        const profileRes = await authMutation("/api/profile", csrfToken, { academic_major: major }, "PATCH");
        if (!profileRes.ok) throw new Error("major");
      }
      const res = await apiFetch("/api/study-plan", { cache: "no-store" });
      if (!res.ok) throw new Error(`Plan failed: ${res.status}`);
      setPlan(await res.json());
      move("plan");
    } catch {
      setError(ar ? "تعذر إنشاء الخطة. تحقق من اختيار التخصص." : "Could not generate the plan. Check the selected major.");
    } finally {
      setLoading(false);
    }
  }

  if (loading && !intervention) {
    return <div className="intervention-loading"><RefreshCw className="spin" size={22} />{ar ? "نبني تدخلًا مخصصًا..." : "Building a targeted intervention..."}</div>;
  }

  if (error && !intervention) {
    return <div className="intervention-error"><CircleAlert size={20} /><span>{error}</span><button onClick={onReset}>{ar ? "ابدأ فحصًا جديدًا" : "Start a new scan"}</button></div>;
  }

  if (!intervention) return null;

  if (phase === "learn") {
    return (
      <div className="intervention-flow">
        <FlowHeader icon={<Target size={18} />} eyebrow={ar ? "تدخل مخصص" : "TARGETED INTERVENTION"} title={ar ? "افهم الفكرة التي سببت الخطأ" : "Repair the model behind the mistake"} />
        <div className="misconception-callout">
          <span>{ar ? "النمط المكتشف" : "DETECTED PATTERN"}</span>
          <b>{misconceptionLabel || intervention.misconception.name}</b>
          <small>{Math.round(intervention.misconception.probability * 100)}% {ar ? "ثقة قبل التدخل" : "pre-intervention confidence"}</small>
        </div>
        <p className="intervention-copy">{ar ? intervention.simple_explanation_ar : intervention.simple_explanation}</p>
        <div className="correct-model-card">
          <div><BrainCircuit size={18} /><b>{ar ? "النموذج الذهني الصحيح" : "Correct mental model"}</b></div>
          <p>{ar ? intervention.correct_model_ar : intervention.correct_model}</p>
        </div>
        <div className="micro-lesson">
          <span><BookOpenCheck size={16} />{ar ? "درس مصغر" : "MICRO-LESSON"}</span>
          {(ar ? intervention.micro_lesson_ar : intervention.micro_lesson).map((step, index) => <div key={step}><i>{index + 1}</i><p>{step}</p></div>)}
        </div>
        <button className="action-button" onClick={() => move("practice")}>{ar ? "اختبر الفهم الجديد" : "Test the repaired model"}<ArrowRight size={18} /></button>
      </div>
    );
  }

  if (phase === "practice") {
    return (
      <div className="intervention-flow">
        <FlowHeader icon={<Sparkles size={18} />} eyebrow={ar ? "سؤال انتقال" : "TRANSFER PRACTICE"} title={ar ? intervention.practice.question_ar : intervention.practice.question} />
        <div className="answer-cards intervention-options">
          {intervention.practice.options.map((option) => (
            <button key={option.value} onClick={() => setAnswer(option.value)} className={answer === option.value ? "selected" : ""}>
              <span>{option.value === "same" ? "=" : option.value}</span><b>{ar ? option.label_ar : option.label}</b>
            </button>
          ))}
        </div>
        <label className="field-label">{ar ? "اشرح لماذا — سيتم تقييم طريقة التفكير" : "Explain why — your reasoning pattern will be evaluated"}</label>
        <textarea className="reasoning-box" value={reasoning} onChange={(event) => setReasoning(event.target.value)} placeholder={ar ? "استخدم النموذج الذهني الجديد في تفسيرك..." : "Use the repaired mental model in your explanation..."} />
        <div className="reasoning-notice"><BrainCircuit size={16} /><span>{ar ? "الإجابة الصحيحة وحدها لا تكفي لتصنيف الفكرة Resolved." : "A correct final answer alone is not enough for a Resolved result."}</span></div>
        {error && <div className="inline-error">{error}</div>}
        <button className="action-button" disabled={!answer || reasoning.trim().length < 5 || loading} onClick={verify}>{loading ? (ar ? "جاري التحقق..." : "Verifying reasoning...") : (ar ? "تحقق من النموذج الذهني" : "Verify the mental model")}<Check size={18} /></button>
      </div>
    );
  }

  if (phase === "verification" && verification) {
    const resolved = verification.status === "resolved";
    return (
      <div className="intervention-flow">
        <FlowHeader icon={resolved ? <BadgeCheck size={18} /> : <CircleAlert size={18} />} eyebrow={ar ? "نتيجة التحقق" : "REASONING VERIFICATION"} title={resolved ? (ar ? "Resolved — تم تصحيح الفكرة" : "Resolved — mental model repaired") : (ar ? "Persistent — الفكرة ما زالت مستمرة" : "Persistent — pattern still detected")} />
        <div className={`verification-hero ${resolved ? "resolved" : "persistent"}`}>
          <strong>{resolved ? "RESOLVED" : "PERSISTENT"}</strong>
          <span>{Math.round(verification.post_misconception_probability * 100)}%</span>
          <small>{ar ? "احتمال الفكرة بعد إعادة التقييم" : "post-verification misconception probability"}</small>
        </div>
        <div className="verification-checks">
          <CheckRow ok={verification.answer_correct} label={ar ? "الإجابة الانتقالية صحيحة" : "Transfer answer is correct"} />
          <CheckRow ok={verification.reasoning_matches_correct_model} label={ar ? "التفسير يستخدم النموذج الصحيح" : "Reasoning uses the correct model"} />
          <CheckRow ok={!verification.same_misconception_detected} label={ar ? "لم يتكرر نمط الفكرة الخاطئة" : "Original misconception pattern is absent"} />
        </div>
        <p className="intervention-copy">{ar ? verification.feedback_ar : verification.feedback}</p>
        {resolved ? (
          <div className="result-actions"><button className="action-button" onClick={onReset}>{ar ? "ابدأ فحصًا آخر" : "Run another scan"}<RefreshCw size={17} /></button><button className="outline-button" onClick={onInsights}>{ar ? "عرض التقدم" : "View progress"}</button></div>
        ) : (
          <div className="major-plan-gate">
            <label>{ar ? "اختر تخصصك لبناء الخطة" : "Select your major to build the plan"}</label>
            <select value={major} onChange={(event) => setMajor(event.target.value)}>
              <option value="">{ar ? "اختر التخصص" : "Choose a major"}</option>
              {majors.map((item) => <option key={item.id} value={item.id}>{ar ? item.label_ar : item.label}</option>)}
            </select>
            {error && <div className="inline-error">{error}</div>}
            <button className="action-button" disabled={!major || loading} onClick={generatePlan}>{loading ? (ar ? "جاري بناء الخطة..." : "Building plan...") : (ar ? "أنشئ خطة مبنية على الفكرة" : "Build misconception-based plan")}<Route size={18} /></button>
          </div>
        )}
      </div>
    );
  }

  if (phase === "plan" && plan) {
    return (
      <div className="intervention-flow study-plan-flow">
        <FlowHeader icon={<ListChecks size={18} />} eyebrow={ar ? "خطة تعلم شخصية" : "MAJOR-AWARE STUDY PLAN"} title={ar ? `ماذا تدرس بعد ذلك — ${plan.major_label}` : `What to study next — ${plan.major_label}`} />
        <div className="plan-progress">
          <div><span>{plan.progress.interventions_completed}</span><small>{ar ? "تدخلات" : "interventions"}</small></div>
          <div><span>{plan.progress.resolved}</span><small>{ar ? "تم حلها" : "resolved"}</small></div>
          <div><span>{plan.progress.persistent}</span><small>{ar ? "مستمرة" : "persistent"}</small></div>
        </div>
        <p className="intervention-copy">{plan.summary}</p>
        <div className="plan-items">
          {plan.items.map((item) => (
            <article key={item.id}>
              <div className="plan-item-head"><i>{String(item.sequence).padStart(2, "0")}</i><div><span>{item.domain} · {item.topic}</span><b>{item.focus}</b></div><em className={item.priority}>{item.priority}</em></div>
              <p>{item.why}</p>
              <ul>{item.activities.map((activity) => <li key={activity}>{activity}</li>)}</ul>
              <small><RefreshCw size={13} />{item.reassessment}</small>
            </article>
          ))}
        </div>
        <div className="reasoning-notice"><BrainCircuit size={16} /><span>{plan.tracking_rule}</span></div>
        <div className="result-actions"><button className="action-button" onClick={onReset}>{ar ? "ابدأ النشاط الأول" : "Start the next activity"}<ArrowRight size={17} /></button><button className="outline-button" onClick={onInsights}>{ar ? "عرض سجل التقدم" : "View progress history"}</button></div>
      </div>
    );
  }

  return null;
}

function FlowHeader({ icon, eyebrow, title }: { icon: React.ReactNode; eyebrow: string; title: string }) {
  return <div className="flow-header"><span>{icon}{eyebrow}</span><h2>{title}</h2></div>;
}

function CheckRow({ ok, label }: { ok: boolean; label: string }) {
  return <div className={ok ? "ok" : "not-ok"}><span>{ok ? <Check size={15} /> : <CircleAlert size={15} />}</span><b>{label}</b></div>;
}

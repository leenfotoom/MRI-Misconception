"use client";

import Link from "next/link";
import { BrainCircuit, ShieldCheck } from "lucide-react";

export default function AuthShell({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <main className="auth-page">
      <section className="auth-brand-panel">
        <Link className="auth-logo" href="/"><span>M</span><b>Misconception MRI</b></Link>
        <div className="auth-brand-copy">
          <span className="auth-eyebrow"><BrainCircuit size={16} /> Cognitive diagnostics platform</span>
          <h1>Learning history that follows the learner.</h1>
          <p>Your account securely connects diagnostic scans, misconception history, progress, and future STEM domains across devices.</p>
          <div className="auth-trust"><ShieldCheck size={18} /><span>Opaque server sessions · Argon2 passwords · hashed verification/reset tokens</span></div>
        </div>
      </section>
      <section className="auth-form-panel">
        <div className="auth-form-wrap">
          <Link href="/" className="auth-back">← Back to platform</Link>
          <h2>{title}</h2>
          <p className="auth-subtitle">{subtitle}</p>
          {children}
        </div>
      </section>
    </main>
  );
}

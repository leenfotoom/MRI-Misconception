"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import AuthShell from "@/components/AuthShell";
import { apiFetch } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [devUrl, setDevUrl] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault(); setLoading(true);
    try {
      const res = await apiFetch("/api/auth/forgot-password", { method: "POST", body: JSON.stringify({ email }) });
      const payload = await res.json();
      setMessage(payload.message);
      setDevUrl(payload.dev_reset_url || "");
    } finally { setLoading(false); }
  }

  return <AuthShell title="Reset your password" subtitle="We will send reset instructions if an eligible account exists."><form className="auth-form" onSubmit={submit}><label>Email<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>{message && <div className="auth-success">{message}{devUrl && <><br /><Link href={devUrl}>Open local reset link</Link></>}</div>}<button className="auth-primary" disabled={loading}>{loading ? "Sending…" : "Send reset instructions"}</button><div className="auth-links"><Link href="/signin">Back to sign in</Link></div></form></AuthShell>;
}

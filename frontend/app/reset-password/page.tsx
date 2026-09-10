"use client";

import { FormEvent, Suspense, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import AuthShell from "@/components/AuthShell";
import { apiFetch, readError } from "@/lib/api";

export default function ResetPasswordPage() {
  return <Suspense fallback={<AuthShell title="Choose a new password" subtitle="Loading secure reset…"><div className="auth-info">Loading…</div></AuthShell>}><ResetPasswordForm /></Suspense>;
}

function ResetPasswordForm() {
  const token = useSearchParams().get("token") || "";
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault(); setError("");
    if (password !== confirm) return setError("Passwords do not match.");
    setLoading(true);
    try {
      const res = await apiFetch("/api/auth/reset-password", { method: "POST", body: JSON.stringify({ token, new_password: password }) });
      if (!res.ok) throw new Error(await readError(res));
      const payload = await res.json(); setMessage(payload.message);
    } catch (err) { setError(err instanceof Error ? err.message : "Reset failed."); }
    finally { setLoading(false); }
  }

  return <AuthShell title="Choose a new password" subtitle="Reset links are single-use and expire automatically."><form className="auth-form" onSubmit={submit}><label>New password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label><label>Confirm password<input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required /></label>{error && <div className="auth-error">{error}</div>}{message && <div className="auth-success">{message}<br /><Link href="/signin">Sign in</Link></div>}<button className="auth-primary" disabled={loading || !token}>{loading ? "Updating…" : "Update password"}</button></form></AuthShell>;
}

"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import AuthShell from "@/components/AuthShell";
import { apiFetch, readError } from "@/lib/api";

export default function VerifyEmailPage() {
  return <Suspense fallback={<AuthShell title="Verify email" subtitle="Preparing secure verification…"><div className="auth-info">Loading…</div></AuthShell>}><VerifyEmailStatus /></Suspense>;
}

function VerifyEmailStatus() {
  const params = useSearchParams();
  const token = params.get("token") || "";
  const [status, setStatus] = useState("Verifying your email…");
  const [ok, setOk] = useState(false);

  useEffect(() => {
    if (!token) { setStatus("Verification token is missing."); return; }
    apiFetch("/api/auth/verify-email", { method: "POST", body: JSON.stringify({ token }) })
      .then(async (res) => {
        if (!res.ok) throw new Error(await readError(res));
        setOk(true); setStatus("Email verified. Your account is ready.");
      })
      .catch((err) => setStatus(err instanceof Error ? err.message : "Verification failed."));
  }, [token]);

  return <AuthShell title="Verify email" subtitle="Email verification protects learner history and account recovery."><div className={ok ? "auth-success" : "auth-info"}>{status}</div>{ok && <Link className="auth-primary auth-link-button" href="/signin">Continue to sign in</Link>}</AuthShell>;
}

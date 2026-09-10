"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";

import AuthShell from "@/components/AuthShell";
import { apiFetch } from "@/lib/api";

export default function SignUpPage() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");

  const [message, setMessage] = useState("");
  const [devUrl, setDevUrl] = useState("");
  const [error, setError] = useState("");

  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();

    setError("");
    setMessage("");
    setDevUrl("");

    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 10) {
      setError("Password must be at least 10 characters.");
      return;
    }

    setLoading(true);

    try {
      const res = await apiFetch("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({
          full_name: fullName,
          email,
          password,
          preferred_language: "en",
        }),
      });

      const payload = await res.json().catch(() => ({}));

      if (!res.ok) {
        const detail = Array.isArray(payload.detail)
          ? payload.detail
              .map((item: { msg?: string }) => item.msg)
              .filter(Boolean)
              .join(", ")
          : payload.detail;

        throw new Error(detail || "Registration failed.");
      }

      setMessage(
        payload.message || "Account created. Check your email."
      );

      setDevUrl(payload.dev_verification_url || "");

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Registration failed."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell
      title="Create your account"
      subtitle="Build a persistent learner profile across devices and future STEM domains."
    >
      <form className="auth-form" onSubmit={submit}>
        <label>
          Full name
          <input
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            autoComplete="name"
            required
          />
        </label>

        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="new-password"
            required
          />
        </label>

        <small className="auth-hint">
          Minimum 10 characters. Use uppercase, lowercase, numbers, and symbols.
        </small>

        <label>
          Confirm password
          <input
            type="password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            autoComplete="new-password"
            required
          />
        </label>

        {error && (
          <div className="auth-error">
            {error}
          </div>
        )}

        {message && (
          <div className="auth-success">
            {message}

            {devUrl && (
              <>
                <br />
                <Link href={devUrl}>
                  Open local verification link
                </Link>
              </>
            )}
          </div>
        )}

        <button
          className="auth-primary"
          disabled={loading || password !== confirm}
        >
          {loading ? "Creating account…" : "Create account"}
        </button>

        <div className="auth-links">
          <span>
            Already have an account?{" "}
            <Link href="/signin">
              Sign in
            </Link>
          </span>
        </div>
      </form>
    </AuthShell>
  );
}
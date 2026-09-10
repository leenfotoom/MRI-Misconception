"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Laptop, LogOut, ShieldCheck, Trash2, UserRound } from "lucide-react";
import AuthShell from "@/components/AuthShell";
import { AuthState, apiFetch, authMutation, getAuthState, readError } from "@/lib/api";

type SessionItem = {
  id: string;
  current: boolean;
  user_agent?: string | null;
  ip_address?: string | null;
  created_at: string;
  last_seen_at: string;
  expires_at: string;
};

export default function AccountPage() {
  const router = useRouter();
  const [auth, setAuth] = useState<AuthState>({ authenticated: false });
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [name, setName] = useState("");
  const [language, setLanguage] = useState("en");
  const [theme, setTheme] = useState("system");
  const [major, setMajor] = useState("undecided");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [deletePassword, setDeletePassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function load() {
    const state = await getAuthState();
    if (!state.authenticated || !state.user) { router.replace("/signin"); return; }
    setAuth(state); setName(state.user.full_name); setLanguage(state.user.preferred_language); setTheme(state.user.preferred_theme); setMajor(state.user.academic_major || "undecided");
    const res = await apiFetch("/api/auth/sessions");
    if (res.ok) setSessions((await res.json()).items || []);
  }

  useEffect(() => { load(); }, []);

  async function saveProfile(e: FormEvent) {
    e.preventDefault(); if (!auth.csrf_token) return; setMessage(""); setError("");
    const res = await authMutation("/api/profile", auth.csrf_token, { full_name: name, preferred_language: language, preferred_theme: theme, ...(major !== "undecided" ? { academic_major: major } : {}) }, "PATCH");
    if (!res.ok) return setError(await readError(res));
    setMessage("Profile updated."); await load();
  }

  async function changePassword(e: FormEvent) {
    e.preventDefault(); if (!auth.csrf_token) return; setMessage(""); setError("");
    const res = await authMutation("/api/auth/change-password", auth.csrf_token, { current_password: currentPassword, new_password: newPassword });
    if (!res.ok) return setError(await readError(res));
    const payload = await res.json(); setAuth((prev) => ({ ...prev, csrf_token: payload.csrf_token })); setCurrentPassword(""); setNewPassword(""); setMessage("Password changed and other sessions were revoked."); await load();
  }

  async function revokeSession(id: string) {
    if (!auth.csrf_token) return;
    const res = await authMutation(`/api/auth/sessions/${id}`, auth.csrf_token, undefined, "DELETE");
    if (!res.ok) return setError(await readError(res));
    const payload = await res.json();
    if (payload.current_session) { router.replace("/signin"); return; }
    await load();
  }

  async function logoutAll() {
    if (!auth.csrf_token) return;
    await authMutation("/api/auth/logout-all", auth.csrf_token);
    router.replace("/signin");
  }

  async function deleteAccount(e: FormEvent) {
    e.preventDefault(); if (!auth.csrf_token) return;
    if (!window.confirm("Delete your account and all diagnostic history? This cannot be undone.")) return;
    const res = await authMutation("/api/profile", auth.csrf_token, { password: deletePassword }, "DELETE");
    if (!res.ok) return setError(await readError(res));
    router.replace("/");
  }

  if (!auth.authenticated || !auth.user) return <AuthShell title="Loading account" subtitle="Checking your secure session…"><div className="auth-info">Loading…</div></AuthShell>;

  return (
    <main className="account-page">
      <header className="account-topbar"><Link href="/" className="auth-logo"><span>M</span><b>Misconception MRI</b></Link><Link className="auth-back" href="/">Back to platform</Link></header>
      <div className="account-wrap">
        <div className="account-heading"><span><UserRound size={18} /> Account</span><h1>{auth.user.full_name}</h1><p>{auth.user.email}</p></div>
        {error && <div className="auth-error">{error}</div>}{message && <div className="auth-success">{message}</div>}

        <section className="account-grid">
          <form className="account-card auth-form" onSubmit={saveProfile}><div className="account-card-title"><UserRound size={18} /><div><b>Profile & preferences</b><small>Synced to your account</small></div></div><label>Full name<input value={name} onChange={(e) => setName(e.target.value)} /></label><label>Academic major<select value={major} onChange={(e) => setMajor(e.target.value)}><option value="undecided">Select later</option><option value="computer_science">Computer Science</option><option value="information_systems">Information Systems</option><option value="engineering">Engineering</option><option value="mathematics">Mathematics</option><option value="natural_sciences">Natural Sciences</option><option value="other">Other / General STEM</option></select></label><label>Language<select value={language} onChange={(e) => setLanguage(e.target.value)}><option value="en">English</option><option value="ar">Arabic</option></select></label><label>Theme<select value={theme} onChange={(e) => setTheme(e.target.value)}><option value="system">System</option><option value="dark">Dark</option><option value="light">Light</option></select></label><button className="auth-primary">Save profile</button></form>

          <form className="account-card auth-form" onSubmit={changePassword}><div className="account-card-title"><ShieldCheck size={18} /><div><b>Security</b><small>Changing your password revokes other sessions</small></div></div><label>Current password<input type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} /></label><label>New password<input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} /></label><button className="auth-primary">Change password</button></form>
        </section>

        <section className="account-card sessions-card"><div className="account-card-title"><Laptop size={18} /><div><b>Active sessions</b><small>Devices currently signed in to your account</small></div><button className="account-text-button" onClick={logoutAll}><LogOut size={15} /> Sign out everywhere</button></div><div className="session-list">{sessions.map((item) => <div className="session-row" key={item.id}><div><b>{item.current ? "Current session" : "Signed-in device"}</b><span>{item.user_agent || "Unknown browser"}</span><small>{item.ip_address || "Unknown IP"} · last active {new Date(item.last_seen_at).toLocaleString()}</small></div><button onClick={() => revokeSession(item.id)}>{item.current ? "Sign out" : "Revoke"}</button></div>)}</div></section>

        <section className="account-card danger-card"><div className="account-card-title"><Trash2 size={18} /><div><b>Delete account</b><small>Permanently deletes your profile, sessions, tokens, and diagnostic history</small></div></div><form className="delete-row" onSubmit={deleteAccount}><input type="password" placeholder="Confirm password" value={deletePassword} onChange={(e) => setDeletePassword(e.target.value)} /><button>Delete account</button></form></section>
      </div>
    </main>
  );
}

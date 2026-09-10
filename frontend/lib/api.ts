export const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type AuthUser = {
  id: string;
  full_name: string;
  email: string;
  is_email_verified: boolean;
  preferred_language: "en" | "ar";
  preferred_theme: "light" | "dark" | "system";
  academic_major: string;
  created_at: string;
};

export type AuthState = {
  authenticated: boolean;
  user?: AuthUser;
  csrf_token?: string;
};

export async function apiFetch(path: string, init: RequestInit = {}) {
  return fetch(`${API}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      ...(init.headers || {}),
    },
  });
}

export async function getAuthState(): Promise<AuthState> {
  const res = await apiFetch("/api/auth/status", { cache: "no-store" });
  if (!res.ok) return { authenticated: false };
  return res.json();
}

export async function authMutation(path: string, csrf: string, body?: unknown, method = "POST") {
  return apiFetch(path, {
    method,
    headers: { "X-CSRF-Token": csrf },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

export async function readError(res: Response): Promise<string> {
  try {
    const payload = await res.json();
    return payload.detail || payload.message || "Request failed.";
  } catch {
    return "Request failed.";
  }
}

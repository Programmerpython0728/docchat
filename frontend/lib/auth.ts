import { apiFetch, clearToken, setToken } from "./api";
import type { TokenResponse, User } from "./types";

export async function login(email: string, password: string): Promise<void> {
  const res = await apiFetch<TokenResponse>("/auth/login/json", {
    method: "POST",
    auth: false,
    body: JSON.stringify({ email, password }),
  });
  setToken(res.access_token);
}

export async function register(
  email: string,
  password: string,
  fullName: string
): Promise<User> {
  return apiFetch<User>("/auth/register", {
    method: "POST",
    auth: false,
    body: JSON.stringify({ email, password, full_name: fullName }),
  });
}

export async function getCurrentUser(): Promise<User> {
  return apiFetch<User>("/auth/me");
}

export function logout() {
  clearToken();
}

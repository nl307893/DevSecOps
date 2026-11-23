import type { TokenPair } from "../types";

const ACCESS_KEY = "access_token";
const REFRESH_KEY = "refresh_token";

export function readTokens(): TokenPair | null {
  const access_token = localStorage.getItem(ACCESS_KEY);
  const refresh_token = localStorage.getItem(REFRESH_KEY);
  if (!access_token || !refresh_token) return null;
  return { access_token, refresh_token, token_type: "Bearer" };
}

export function writeTokens(tokens: TokenPair): void {
  localStorage.setItem(ACCESS_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

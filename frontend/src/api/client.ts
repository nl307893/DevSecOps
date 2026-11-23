import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

import { clearTokens, readTokens, writeTokens } from "../auth/storage";
import type { TokenPair } from "../types";

export const API_ORIGIN = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:5000";

export const api = axios.create({
  baseURL: `${API_ORIGIN}/api`,
});

type RetryConfig = InternalAxiosRequestConfig & { _retry?: boolean };

let refreshPromise: Promise<string> | null = null;

export const AUTH_LOGOUT_EVENT = "auth:logout";

function isPublicAuth(url: string | undefined): boolean {
  if (!url) return false;
  return (
    url.includes("/auth/login") ||
    url.includes("/auth/register") ||
    url.includes("/auth/refresh") ||
    url.includes("/auth/logout")
  );
}

async function refreshAccessToken(): Promise<string> {
  const tokens = readTokens();
  if (!tokens) throw new Error("No refresh token");
  const response = await axios.post<TokenPair>(`${API_ORIGIN}/api/auth/refresh`, {
    refresh_token: tokens.refresh_token,
  });
  writeTokens(response.data);
  return response.data.access_token;
}

api.interceptors.request.use((config) => {
  const tokens = readTokens();
  if (tokens && !isPublicAuth(config.url)) {
    config.headers.Authorization = `Bearer ${tokens.access_token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetryConfig | undefined;
    if (
      error.response?.status !== 401 ||
      !original ||
      original._retry ||
      isPublicAuth(original.url)
    ) {
      return Promise.reject(error);
    }
    original._retry = true;
    try {
      refreshPromise ??= refreshAccessToken().finally(() => {
        refreshPromise = null;
      });
      const accessToken = await refreshPromise;
      original.headers.Authorization = `Bearer ${accessToken}`;
      return api.request(original);
    } catch (refreshError) {
      clearTokens();
      window.dispatchEvent(new Event(AUTH_LOGOUT_EVENT));
      return Promise.reject(refreshError);
    }
  },
);

export function apiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data;
    if (
      data &&
      typeof data === "object" &&
      "error" in data &&
      typeof data.error === "string"
    ) {
      return data.error;
    }
    if (!error.response) return "Cannot reach the server";
  }
  return "Something went wrong";
}

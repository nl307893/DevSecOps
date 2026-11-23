import axios from "axios";

import { clearTokens, readTokens, writeTokens } from "../auth/storage";
import type { TokenPair } from "../types";
import { API_ORIGIN } from "./client";

export interface RegisterInput {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export async function login(email: string, password: string): Promise<TokenPair> {
  const response = await axios.post<TokenPair>(`${API_ORIGIN}/api/auth/login`, {
    email,
    password,
  });
  writeTokens(response.data);
  return response.data;
}

export async function register(input: RegisterInput): Promise<TokenPair> {
  const response = await axios.post<TokenPair>(
    `${API_ORIGIN}/api/auth/register`,
    input,
  );
  writeTokens(response.data);
  return response.data;
}

export async function logout(): Promise<void> {
  const tokens = readTokens();
  clearTokens();
  if (!tokens) return;
  await axios
    .post(`${API_ORIGIN}/api/auth/logout`, { refresh_token: tokens.refresh_token })
    .catch(() => undefined);
}

import type { UserProfile } from "../types";
import { api } from "./client";

export async function getMe(): Promise<UserProfile> {
  const response = await api.get<UserProfile>("/users/me");
  return response.data;
}

export async function updateName(
  first_name: string,
  last_name: string,
): Promise<UserProfile> {
  const response = await api.patch<UserProfile>("/users/me/name", {
    first_name,
    last_name,
  });
  return response.data;
}

export async function updateEmail(email: string): Promise<UserProfile> {
  const response = await api.patch<UserProfile>("/users/me/email", { email });
  return response.data;
}

export async function updatePassword(
  current_password: string,
  new_password: string,
): Promise<void> {
  await api.patch("/users/me/password", { current_password, new_password });
}

export async function deleteAccount(password: string): Promise<void> {
  await api.delete("/users/me", { data: { password } });
}

import type { AccessClaims, Role } from "../types";

function isRole(value: unknown): value is Role {
  return value === "client" || value === "technician";
}

export function decodeAccessToken(token: string): AccessClaims | null {
  const payload = token.split(".")[1];
  if (!payload) return null;
  try {
    const padded = payload.replace(/-/g, "+").replace(/_/g, "/");
    const json = atob(padded.padEnd(padded.length + ((4 - (padded.length % 4)) % 4), "="));
    const data = JSON.parse(json) as Partial<AccessClaims>;
    if (typeof data.sub !== "string" || !isRole(data.role)) return null;
    return {
      sub: data.sub,
      role: data.role,
      exp: typeof data.exp === "number" ? data.exp : 0,
    };
  } catch {
    return null;
  }
}

export function homePath(role: Role): string {
  return role === "technician" ? "/technician/tickets" : "/tickets";
}

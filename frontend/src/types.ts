export type Role = "client" | "technician";

export type TicketStatus =
  | "new"
  | "instatus"
  | "resolved"
  | "cancelled"
  | "archived";

export type TicketCategory =
  | "hardware"
  | "software"
  | "network"
  | "access"
  | "other";

export type Priority = "low" | "medium" | "high";

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AccessClaims {
  sub: string;
  role: Role;
  exp: number;
}

export interface UserProfile {
  id: string;
  first_name: string | null;
  last_name: string | null;
  display_name: string;
  email: string;
  role: Role;
}

export interface Ticket {
  id: string;
  title: string;
  description: string;
  category: TicketCategory;
  status: TicketStatus;
  client_name: string;
  technician_name: string | null;
  created_at: string | null;
  priority?: Priority;
}

export interface Comment {
  id: string;
  content: string;
  author_name: string;
  created_at: string | null;
}

export interface TicketHistoryEntry {
  id: string;
  old_status: TicketStatus | null;
  new_status: TicketStatus;
  changed_by: string;
  changed_at: string | null;
}

export const CATEGORIES: TicketCategory[] = [
  "hardware",
  "software",
  "network",
  "access",
  "other",
];

export const STATUSES: TicketStatus[] = [
  "new",
  "instatus",
  "resolved",
  "cancelled",
  "archived",
];

export const PRIORITIES: Priority[] = ["low", "medium", "high"];

export const CLOSED_COMMENT_STATUSES: TicketStatus[] = [
  "resolved",
  "cancelled",
  "archived",
];

export function statusLabel(status: TicketStatus): string {
  if (status === "instatus") return "In progress";
  return status.charAt(0).toUpperCase() + status.slice(1);
}

export function formatWhen(value: string | null): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

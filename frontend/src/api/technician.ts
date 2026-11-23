import type {
  Comment,
  Priority,
  Ticket,
  TicketCategory,
  TicketHistoryEntry,
  TicketStatus,
} from "../types";
import { api } from "./client";

export async function listAllTickets(): Promise<Ticket[]> {
  const response = await api.get<Ticket[]>("/technician/tickets");
  return response.data;
}

export async function listAssignedTickets(): Promise<Ticket[]> {
  const response = await api.get<Ticket[]>("/technician/tickets/assigned");
  return response.data;
}

export async function getTechnicianTicket(id: string): Promise<Ticket> {
  const response = await api.get<Ticket>(`/technician/tickets/${id}`);
  return response.data;
}

export async function getTicketHistory(id: string): Promise<TicketHistoryEntry[]> {
  const response = await api.get<TicketHistoryEntry[]>(
    `/technician/tickets/${id}/history`,
  );
  return response.data;
}

export async function listTechnicianComments(id: string): Promise<Comment[]> {
  const response = await api.get<Comment[]>(`/technician/tickets/${id}/comments`);
  return response.data;
}

export async function addTechnicianComment(
  id: string,
  content: string,
): Promise<Comment> {
  const response = await api.post<Comment>(`/technician/tickets/${id}/comments`, {
    content,
  });
  return response.data;
}

export async function assignToMe(id: string): Promise<Ticket> {
  const response = await api.patch<Ticket>(`/technician/tickets/${id}/assign`, {});
  return response.data;
}

export async function updatePriority(id: string, priority: Priority): Promise<Ticket> {
  const response = await api.patch<Ticket>(`/technician/tickets/${id}/priority`, {
    priority,
  });
  return response.data;
}

export async function updateCategory(
  id: string,
  category: TicketCategory,
): Promise<Ticket> {
  const response = await api.patch<Ticket>(`/technician/tickets/${id}/category`, {
    category,
  });
  return response.data;
}

export async function updateStatus(id: string, status: TicketStatus): Promise<Ticket> {
  const response = await api.patch<Ticket>(`/technician/tickets/${id}/status`, {
    status,
  });
  return response.data;
}

export async function archiveTicket(id: string): Promise<Ticket> {
  const response = await api.patch<Ticket>(`/technician/tickets/${id}/archive`);
  return response.data;
}

import type { Comment, Ticket, TicketCategory } from "../types";
import { api } from "./client";

export interface TicketInput {
  title: string;
  description: string;
  category: TicketCategory;
}

export async function listTickets(): Promise<Ticket[]> {
  const response = await api.get<Ticket[]>("/tickets");
  return response.data;
}

export async function getTicket(id: string): Promise<Ticket> {
  const response = await api.get<Ticket>(`/tickets/${id}`);
  return response.data;
}

export async function createTicket(input: TicketInput): Promise<Ticket> {
  const response = await api.post<Ticket>("/tickets", input);
  return response.data;
}

export async function updateTicket(
  id: string,
  input: Partial<TicketInput>,
): Promise<Ticket> {
  const response = await api.patch<Ticket>(`/tickets/${id}`, input);
  return response.data;
}

export async function deleteTicket(id: string): Promise<void> {
  await api.delete(`/tickets/${id}`);
}

export async function listComments(id: string): Promise<Comment[]> {
  const response = await api.get<Comment[]>(`/tickets/${id}/comments`);
  return response.data;
}

export async function addComment(id: string, content: string): Promise<Comment> {
  const response = await api.post<Comment>(`/tickets/${id}/comments`, { content });
  return response.data;
}

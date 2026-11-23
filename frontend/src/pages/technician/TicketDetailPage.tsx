import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { apiErrorMessage } from "../../api/client";
import {
  addTechnicianComment,
  archiveTicket,
  assignToMe,
  getTechnicianTicket,
  getTicketHistory,
  listTechnicianComments,
  updateCategory,
  updatePriority,
  updateStatus,
} from "../../api/technician";
import { Comments } from "../../components/Comments";
import {
  CATEGORIES,
  CLOSED_COMMENT_STATUSES,
  formatWhen,
  PRIORITIES,
  STATUSES,
  statusLabel,
  type Comment,
  type Priority,
  type Ticket,
  type TicketCategory,
  type TicketHistoryEntry,
  type TicketStatus,
} from "../../types";

export function TechnicianTicketDetailPage() {
  const { id = "" } = useParams();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [history, setHistory] = useState<TicketHistoryEntry[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    Promise.all([
      getTechnicianTicket(id),
      listTechnicianComments(id),
      getTicketHistory(id),
    ])
      .then(([loaded, loadedComments, loadedHistory]) => {
        setTicket(loaded);
        setComments(loadedComments);
        setHistory(loadedHistory);
      })
      .catch((loadError) => setError(apiErrorMessage(loadError)))
      .finally(() => setLoading(false));
  }, [id]);

  async function run(action: () => Promise<Ticket>, reloadHistory = false) {
    setError("");
    setPending(true);
    try {
      setTicket(await action());
      if (reloadHistory) setHistory(await getTicketHistory(id));
    } catch (actionError) {
      setError(apiErrorMessage(actionError));
    } finally {
      setPending(false);
    }
  }

  if (loading) return <p className="page-message">Loading ticket…</p>;
  if (!ticket) {
    return (
      <main className="page stack">
        <p className="error">{error || "Ticket not found"}</p>
        <Link to="/technician/tickets">Back to tickets</Link>
      </main>
    );
  }

  const canComment = !CLOSED_COMMENT_STATUSES.includes(ticket.status);

  return (
    <main className="page stack">
      <Link to="/technician/tickets">Back to tickets</Link>
      <div className="ticket-card-head">
        <h1>{ticket.title}</h1>
        <span className={`badge status-${ticket.status}`}>{statusLabel(ticket.status)}</span>
      </div>
      <p className="muted">
        Client {ticket.client_name}
        {ticket.technician_name ? ` · Technician ${ticket.technician_name}` : " · Unassigned"}
        {" · "}
        {formatWhen(ticket.created_at)}
      </p>
      <p className="description">{ticket.description}</p>
      {error && <p className="error">{error}</p>}

      <section className="card stack">
        <h2>Actions</h2>
        <div className="button-row">
          <button className="button" type="button" disabled={pending} onClick={() => run(() => assignToMe(id), true)}>
            Assign to me
          </button>
          <button
            className="button"
            type="button"
            disabled={pending || ticket.status === "archived"}
            onClick={() => run(() => archiveTicket(id), true)}
          >
            Archive
          </button>
        </div>
        <label>
          Priority
          <select
            value={ticket.priority ?? "medium"}
            disabled={pending}
            onChange={(event) => run(() => updatePriority(id, event.target.value as Priority))}
          >
            {PRIORITIES.map((priority) => (
              <option key={priority} value={priority}>{priority}</option>
            ))}
          </select>
        </label>
        <label>
          Category
          <select
            value={ticket.category}
            disabled={pending}
            onChange={(event) => run(() => updateCategory(id, event.target.value as TicketCategory))}
          >
            {CATEGORIES.map((category) => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </label>
        <label>
          Status
          <select
            value={ticket.status}
            disabled={pending}
            onChange={(event) => run(() => updateStatus(id, event.target.value as TicketStatus), true)}
          >
            {STATUSES.map((status) => (
              <option key={status} value={status}>{statusLabel(status)}</option>
            ))}
          </select>
        </label>
      </section>

      <section className="stack">
        <h2>Status history</h2>
        {history.length === 0 && <p className="muted">No status changes yet.</p>}
        <ul className="comment-list">
          {history.map((entry) => (
            <li key={entry.id} className="comment">
              <div className="comment-meta">
                <strong>
                  {entry.old_status ? statusLabel(entry.old_status) : "Created"} → {statusLabel(entry.new_status)}
                </strong>
                <span>{formatWhen(entry.changed_at)}</span>
              </div>
              <p className="muted">{entry.changed_by}</p>
            </li>
          ))}
        </ul>
      </section>

      <Comments
        comments={comments}
        canComment={canComment}
        onSubmit={async (content) => {
          try {
            const created = await addTechnicianComment(id, content);
            setComments((current) => [...current, created]);
          } catch (submitError) {
            throw new Error(apiErrorMessage(submitError));
          }
        }}
      />
    </main>
  );
}

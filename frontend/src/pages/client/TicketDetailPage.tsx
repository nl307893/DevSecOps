import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { apiErrorMessage } from "../../api/client";
import {
  addComment,
  deleteTicket,
  getTicket,
  listComments,
  updateTicket,
} from "../../api/tickets";
import { Comments } from "../../components/Comments";
import {
  CATEGORIES,
  CLOSED_COMMENT_STATUSES,
  formatWhen,
  statusLabel,
  type Comment,
  type Ticket,
  type TicketCategory,
} from "../../types";

export function TicketDetailPage() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<TicketCategory>("other");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getTicket(id), listComments(id)])
      .then(([loaded, loadedComments]) => {
        setTicket(loaded);
        setTitle(loaded.title);
        setDescription(loaded.description);
        setCategory(loaded.category);
        setComments(loadedComments);
      })
      .catch((loadError) => setError(apiErrorMessage(loadError)))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <p className="page-message">Loading ticket…</p>;
  if (!ticket) {
    return (
      <main className="page stack">
        <p className="error">{error || "Ticket not found"}</p>
        <Link to="/tickets">Back to tickets</Link>
      </main>
    );
  }

  const canEdit = ticket.status === "new" && !ticket.technician_name;
  const canComment = !CLOSED_COMMENT_STATUSES.includes(ticket.status);

  async function save(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const updated = await updateTicket(id, { title, description, category });
      setTicket(updated);
    } catch (submitError) {
      setError(apiErrorMessage(submitError));
    }
  }

  async function remove() {
    if (!window.confirm("Delete this ticket?")) return;
    setError("");
    try {
      await deleteTicket(id);
      navigate("/tickets");
    } catch (submitError) {
      setError(apiErrorMessage(submitError));
    }
  }

  return (
    <main className="page stack">
      <Link to="/tickets">Back to tickets</Link>
      <div className="ticket-card-head">
        <h1>{ticket.title}</h1>
        <span className={`badge status-${ticket.status}`}>{statusLabel(ticket.status)}</span>
      </div>
      <p className="muted">
        {ticket.category} · {formatWhen(ticket.created_at)}
        {ticket.technician_name ? ` · Technician ${ticket.technician_name}` : ""}
      </p>
      <p className="description">{ticket.description}</p>
      {error && <p className="error">{error}</p>}

      {canEdit && (
        <form className="card stack" onSubmit={save}>
          <h2>Edit ticket</h2>
          <label>
            Title
            <input value={title} onChange={(event) => setTitle(event.target.value)} required maxLength={255} />
          </label>
          <label>
            Description
            <textarea value={description} onChange={(event) => setDescription(event.target.value)} required />
          </label>
          <label>
            Category
            <select value={category} onChange={(event) => setCategory(event.target.value as TicketCategory)}>
              {CATEGORIES.map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>
          <div className="button-row">
            <button className="button" type="submit">Save changes</button>
            <button className="button danger" type="button" onClick={remove}>Delete ticket</button>
          </div>
        </form>
      )}

      <Comments
        comments={comments}
        canComment={canComment}
        onSubmit={async (content) => {
          try {
            const created = await addComment(id, content);
            setComments((current) => [...current, created]);
          } catch (submitError) {
            throw new Error(apiErrorMessage(submitError));
          }
        }}
      />
    </main>
  );
}

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiErrorMessage } from "../../api/client";
import { listTickets } from "../../api/tickets";
import { formatWhen, statusLabel, type Ticket } from "../../types";

export function TicketListPage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listTickets()
      .then(setTickets)
      .catch((loadError) => setError(apiErrorMessage(loadError)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="page stack">
      <div className="page-heading">
        <h1>My tickets</h1>
        <Link className="button" to="/tickets/new">New ticket</Link>
      </div>
      {loading && <p>Loading tickets…</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && tickets.length === 0 && (
        <p className="muted">You have no tickets yet.</p>
      )}
      <div className="stack">
        {tickets.map((ticket) => (
          <article key={ticket.id} className="card ticket-card">
            <div className="ticket-card-head">
              <h2>{ticket.title}</h2>
              <span className={`badge status-${ticket.status}`}>{statusLabel(ticket.status)}</span>
            </div>
            <p className="muted">
              {ticket.category} · {formatWhen(ticket.created_at)}
              {ticket.technician_name ? ` · ${ticket.technician_name}` : ""}
            </p>
            <Link to={`/tickets/${ticket.id}`}>Open</Link>
          </article>
        ))}
      </div>
    </main>
  );
}

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiErrorMessage } from "../../api/client";
import { listAllTickets, listAssignedTickets } from "../../api/technician";
import { formatWhen, statusLabel, type Ticket } from "../../types";

export function TechnicianTicketListPage({ assigned }: { assigned: boolean }) {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = assigned ? listAssignedTickets : listAllTickets;
    load()
      .then(setTickets)
      .catch((loadError) => setError(apiErrorMessage(loadError)))
      .finally(() => setLoading(false));
  }, [assigned]);

  return (
    <main className="page stack">
      <h1>{assigned ? "Assigned to me" : "All tickets"}</h1>
      {loading && <p>Loading tickets…</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && tickets.length === 0 && (
        <p className="muted">No tickets to show.</p>
      )}
      <div className="stack">
        {tickets.map((ticket) => (
          <article key={ticket.id} className="card ticket-card">
            <div className="ticket-card-head">
              <h2>{ticket.title}</h2>
              <span className={`badge status-${ticket.status}`}>{statusLabel(ticket.status)}</span>
            </div>
            <p className="muted">
              {ticket.category}
              {ticket.priority ? ` · ${ticket.priority} priority` : ""}
              {" · "}
              {ticket.client_name}
              {ticket.technician_name ? ` · ${ticket.technician_name}` : " · unassigned"}
              {" · "}
              {formatWhen(ticket.created_at)}
            </p>
            <Link to={`/technician/tickets/${ticket.id}`}>Open</Link>
          </article>
        ))}
      </div>
    </main>
  );
}

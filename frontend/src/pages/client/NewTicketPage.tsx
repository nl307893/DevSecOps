import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { apiErrorMessage } from "../../api/client";
import { createTicket } from "../../api/tickets";
import { CATEGORIES, type TicketCategory } from "../../types";

export function NewTicketPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<TicketCategory>("hardware");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setPending(true);
    try {
      const ticket = await createTicket({ title, description, category });
      navigate(`/tickets/${ticket.id}`);
    } catch (submitError) {
      setError(apiErrorMessage(submitError));
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="page">
      <form className="card stack" onSubmit={handleSubmit}>
        <h1>New ticket</h1>
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
          <select
            value={category}
            onChange={(event) => setCategory(event.target.value as TicketCategory)}
          >
            {CATEGORIES.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        </label>
        {error && <p className="error">{error}</p>}
        <button className="button" type="submit" disabled={pending}>
          {pending ? "Creating…" : "Create ticket"}
        </button>
      </form>
    </main>
  );
}

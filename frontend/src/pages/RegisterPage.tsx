import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { apiErrorMessage } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (password.length < 12) {
      setError("Password must be at least 12 characters");
      return;
    }
    setError("");
    setPending(true);
    try {
      await register({
        email,
        password,
        first_name: firstName,
        last_name: lastName,
      });
      navigate("/tickets");
    } catch (submitError) {
      setError(apiErrorMessage(submitError));
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="auth-layout">
      <form className="card stack" onSubmit={handleSubmit}>
        <h1>Create a client account</h1>
        <label>
          First name
          <input
            value={firstName}
            onChange={(event) => setFirstName(event.target.value)}
            required
            maxLength={100}
          />
        </label>
        <label>
          Last name
          <input
            value={lastName}
            onChange={(event) => setLastName(event.target.value)}
            required
            maxLength={100}
          />
        </label>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
            autoComplete="email"
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
            minLength={12}
            autoComplete="new-password"
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="button" type="submit" disabled={pending}>
          {pending ? "Creating…" : "Create account"}
        </button>
        <p className="muted">
          Already registered? <Link to="/login">Sign in</Link>
        </p>
      </form>
    </main>
  );
}

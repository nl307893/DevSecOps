import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { apiErrorMessage } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { homePath } from "../auth/jwt";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setPending(true);
    try {
      const profile = await login(email, password);
      navigate(homePath(profile.role));
    } catch (submitError) {
      setError(apiErrorMessage(submitError));
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="auth-layout">
      <form className="card stack" onSubmit={handleSubmit}>
        <h1>Sign in</h1>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
            autoComplete="username"
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
            autoComplete="current-password"
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="button" type="submit" disabled={pending}>
          {pending ? "Signing in…" : "Sign in"}
        </button>
        <p className="muted">
          New client? <Link to="/register">Create an account</Link>
        </p>
      </form>
    </main>
  );
}

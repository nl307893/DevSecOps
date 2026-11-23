import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { apiErrorMessage } from "../api/client";
import { deleteAccount, updateEmail, updateName, updatePassword } from "../api/users";
import { useAuth } from "../auth/AuthContext";

export function ProfilePage() {
  const { profile, setProfile, logout } = useAuth();
  const navigate = useNavigate();
  const [firstName, setFirstName] = useState(profile?.first_name ?? "");
  const [lastName, setLastName] = useState(profile?.last_name ?? "");
  const [email, setEmail] = useState(profile?.email ?? "");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [deletePassword, setDeletePassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  if (!profile) return <p className="page-message">Loading profile…</p>;

  async function saveName(event: FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      setProfile(await updateName(firstName, lastName));
      setMessage("Name updated.");
    } catch (submitError) {
      setError(apiErrorMessage(submitError));
    }
  }

  async function saveEmail(event: FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      setProfile(await updateEmail(email));
      setMessage("Email updated.");
    } catch (submitError) {
      setError(apiErrorMessage(submitError));
    }
  }

  async function savePassword(event: FormEvent) {
    event.preventDefault();
    if (newPassword.length < 8) {
      setError("New password must be at least 8 characters");
      return;
    }
    setError("");
    setMessage("");
    try {
      await updatePassword(currentPassword, newPassword);
      setCurrentPassword("");
      setNewPassword("");
      setMessage("Password updated.");
    } catch (submitError) {
      setError(apiErrorMessage(submitError));
    }
  }

  async function removeAccount(event: FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      await deleteAccount(deletePassword);
      await logout();
      navigate("/login");
    } catch (submitError) {
      setError(apiErrorMessage(submitError));
    }
  }

  return (
    <main className="page stack">
      <h1>Profile</h1>
      <p className="muted">
        Signed in as {profile.role}. {profile.email}
      </p>
      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}

      <form className="card stack" onSubmit={saveName}>
        <h2>Name</h2>
        <label>
          First name
          <input value={firstName} onChange={(event) => setFirstName(event.target.value)} required maxLength={100} />
        </label>
        <label>
          Last name
          <input value={lastName} onChange={(event) => setLastName(event.target.value)} required maxLength={100} />
        </label>
        <button className="button" type="submit">Save name</button>
      </form>

      <form className="card stack" onSubmit={saveEmail}>
        <h2>Email</h2>
        <label>
          Email
          <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        </label>
        <button className="button" type="submit">Save email</button>
      </form>

      <form className="card stack" onSubmit={savePassword}>
        <h2>Password</h2>
        <label>
          Current password
          <input type="password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} required autoComplete="current-password" />
        </label>
        <label>
          New password
          <input type="password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} required minLength={8} autoComplete="new-password" />
        </label>
        <button className="button" type="submit">Change password</button>
      </form>

      <form className="card stack danger-card" onSubmit={removeAccount}>
        <h2>Delete account</h2>
        <label>
          Confirm with your password
          <input type="password" value={deletePassword} onChange={(event) => setDeletePassword(event.target.value)} required autoComplete="current-password" />
        </label>
        <button className="button danger" type="submit">Delete account</button>
      </form>
    </main>
  );
}

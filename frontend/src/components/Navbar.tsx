import { NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export function Navbar() {
  const { claims, profile, logout } = useAuth();
  const navigate = useNavigate();
  const role = claims?.role;

  async function onLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <header className="navbar">
      <NavLink to={role === "technician" ? "/technician/tickets" : "/tickets"} className="brand">
        Service desk
      </NavLink>
      <nav>
        {role === "client" && (
          <>
            <NavLink to="/tickets" end>
              My tickets
            </NavLink>
            <NavLink to="/tickets/new">New ticket</NavLink>
          </>
        )}
        {role === "technician" && (
          <>
            <NavLink to="/technician/tickets" end>
              All tickets
            </NavLink>
            <NavLink to="/technician/tickets/assigned">Assigned to me</NavLink>
          </>
        )}
        <NavLink to="/profile">Profile</NavLink>
      </nav>
      <div className="navbar-user">
        <span>{profile?.display_name ?? "Account"}</span>
        <button type="button" className="button ghost" onClick={onLogout}>
          Log out
        </button>
      </div>
    </header>
  );
}

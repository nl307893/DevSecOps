import { Navigate, Outlet } from "react-router-dom";

import { homePath } from "../auth/jwt";
import { useAuth } from "../auth/AuthContext";
import type { Role } from "../types";

export function RequireAuth() {
  const { ready, claims } = useAuth();
  if (!ready) return <p className="page-message">Loading…</p>;
  if (!claims) return <Navigate to="/login" replace />;
  return <Outlet />;
}

export function RequireRole({ role }: { role: Role }) {
  const { claims } = useAuth();
  if (!claims) return <Navigate to="/login" replace />;
  if (claims.role !== role) return <Navigate to={homePath(claims.role)} replace />;
  return <Outlet />;
}

export function GuestOnly() {
  const { ready, claims } = useAuth();
  if (!ready) return <p className="page-message">Loading…</p>;
  if (claims) return <Navigate to={homePath(claims.role)} replace />;
  return <Outlet />;
}

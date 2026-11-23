import { Navigate, Outlet, Route, Routes } from "react-router-dom";

import { useAuth } from "./auth/AuthContext";
import { homePath } from "./auth/jwt";
import { Navbar } from "./components/Navbar";
import { GuestOnly, RequireAuth, RequireRole } from "./components/ProtectedRoute";
import { NewTicketPage } from "./pages/client/NewTicketPage";
import { TicketDetailPage } from "./pages/client/TicketDetailPage";
import { TicketListPage } from "./pages/client/TicketListPage";
import { LoginPage } from "./pages/LoginPage";
import { ProfilePage } from "./pages/ProfilePage";
import { RegisterPage } from "./pages/RegisterPage";
import { TechnicianTicketDetailPage } from "./pages/technician/TicketDetailPage";
import { TechnicianTicketListPage } from "./pages/technician/TicketListPage";

function HomeRedirect() {
  const { ready, claims } = useAuth();
  if (!ready) return <p className="page-message">Loading…</p>;
  if (!claims) return <Navigate to="/login" replace />;
  return <Navigate to={homePath(claims.role)} replace />;
}

function AppShell() {
  return (
    <>
      <Navbar />
      <Outlet />
    </>
  );
}

export function App() {
  return (
    <Routes>
      <Route element={<GuestOnly />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>
      <Route element={<RequireAuth />}>
        <Route element={<AppShell />}>
          <Route element={<RequireRole role="client" />}>
            <Route path="/tickets" element={<TicketListPage />} />
            <Route path="/tickets/new" element={<NewTicketPage />} />
            <Route path="/tickets/:id" element={<TicketDetailPage />} />
          </Route>
          <Route element={<RequireRole role="technician" />}>
            <Route path="/technician/tickets" element={<TechnicianTicketListPage assigned={false} />} />
            <Route path="/technician/tickets/assigned" element={<TechnicianTicketListPage assigned />} />
            <Route path="/technician/tickets/:id" element={<TechnicianTicketDetailPage />} />
          </Route>
          <Route path="/profile" element={<ProfilePage />} />
        </Route>
      </Route>
      <Route path="*" element={<HomeRedirect />} />
    </Routes>
  );
}

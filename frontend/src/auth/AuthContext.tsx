import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import * as authApi from "../api/auth";
import type { RegisterInput } from "../api/auth";
import { AUTH_LOGOUT_EVENT } from "../api/client";
import { getMe } from "../api/users";
import type { AccessClaims, UserProfile } from "../types";
import { decodeAccessToken } from "./jwt";
import { readTokens } from "./storage";

interface AuthState {
  ready: boolean;
  claims: AccessClaims | null;
  profile: UserProfile | null;
  login: (email: string, password: string) => Promise<UserProfile>;
  register: (input: RegisterInput) => Promise<UserProfile>;
  logout: () => Promise<void>;
  setProfile: (profile: UserProfile) => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);
  const [claims, setClaims] = useState<AccessClaims | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);

  async function loadProfile(): Promise<UserProfile> {
    const tokens = readTokens();
    const nextClaims = tokens ? decodeAccessToken(tokens.access_token) : null;
    setClaims(nextClaims);
    if (!nextClaims) {
      setProfile(null);
      throw new Error("Invalid session");
    }
    const me = await getMe();
    setProfile(me);
    const refreshed = readTokens();
    setClaims(refreshed ? decodeAccessToken(refreshed.access_token) : nextClaims);
    return me;
  }

  useEffect(() => {
    const tokens = readTokens();
    if (!tokens || !decodeAccessToken(tokens.access_token)) {
      setReady(true);
      return;
    }
    loadProfile()
      .catch(() => {
        setClaims(null);
        setProfile(null);
      })
      .finally(() => setReady(true));

    function onLogout() {
      setClaims(null);
      setProfile(null);
    }
    window.addEventListener(AUTH_LOGOUT_EVENT, onLogout);
    return () => window.removeEventListener(AUTH_LOGOUT_EVENT, onLogout);
  }, []);

  const value: AuthState = {
    ready,
    claims,
    profile,
    async login(email, password) {
      await authApi.login(email, password);
      return loadProfile();
    },
    async register(input) {
      await authApi.register(input);
      return loadProfile();
    },
    async logout() {
      await authApi.logout();
      setClaims(null);
      setProfile(null);
    },
    setProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

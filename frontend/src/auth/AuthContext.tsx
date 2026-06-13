import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { getMe } from "../api/boardApi";
import type { User } from "../api/types";
import {
  clearAccessToken,
  getAccessToken,
  saveAccessToken,
} from "./tokenStorage";

type AuthContextValue = {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  applyLogin: (token: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getAccessToken());
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(Boolean(token));

  const logout = useCallback(() => {
    clearAccessToken();
    setToken(null);
    setUser(null);
    setIsLoading(false);
  }, []);

  const loadCurrentUser = useCallback(
    async (accessToken: string) => {
      try {
        setIsLoading(true);
        const currentUser = await getMe(accessToken);
        setUser(currentUser);
      } catch {
        logout();
      } finally {
        setIsLoading(false);
      }
    },
    [logout],
  );

  const applyLogin = useCallback(
    async (accessToken: string) => {
      saveAccessToken(accessToken);
      setToken(accessToken);
      await loadCurrentUser(accessToken);
    },
    [loadCurrentUser],
  );

  useEffect(() => {
    if (token) {
      void loadCurrentUser(token);
    }
  }, [loadCurrentUser, token]);

  const value = useMemo(
    () => ({
      user,
      token,
      isLoading,
      isAuthenticated: Boolean(user && token),
      applyLogin,
      logout,
    }),
    [applyLogin, isLoading, logout, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth는 AuthProvider 안에서만 사용할 수 있습니다.");
  }

  return context;
}

"use client";

import { useCallback, useState } from "react";
import { useAuthStore } from "@/store/authStore";
import { authApi } from "@/lib/api/auth";
import type { LoginPayload } from "@/lib/api/auth";

export function useAuth() {
  const { user, accessToken, refreshToken, setTokens, setUser, logout: storeLogout } =
    useAuthStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(
    async (payload: LoginPayload) => {
      setLoading(true);
      setError(null);
      try {
        const data = await authApi.login(payload);
        setTokens({ access: data.access, refresh: data.refresh });
        setUser(data.user);
        return data.user;
      } catch (err: unknown) {
        const msg =
          (err as { response?: { data?: { detail?: string } } })?.response?.data
            ?.detail ?? "Login failed. Please check your credentials.";
        setError(msg);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [setTokens, setUser]
  );

  const logout = useCallback(async () => {
    if (refreshToken) {
      try {
        await authApi.logout(refreshToken);
      } catch {
        // Best-effort — always clear local state
      }
    }
    storeLogout();
  }, [refreshToken, storeLogout]);

  return {
    user,
    accessToken,
    loading,
    error,
    isAuthenticated: !!accessToken,
    login,
    logout,
  };
}

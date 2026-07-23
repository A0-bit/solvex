import apiClient from "./client";
import type { AuthResponse, User } from "@/types/user";

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  password2: string;
  phone?: string;
  role?: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface ChangePasswordPayload {
  old_password: string;
  new_password: string;
}

export const authApi = {
  register: (payload: RegisterPayload) =>
    apiClient.post<User>("/auth/register/", payload).then((r) => r.data),

  login: (payload: LoginPayload) =>
    apiClient.post<AuthResponse>("/auth/login/", payload).then((r) => r.data),

  logout: (refreshToken: string) =>
    apiClient
      .post("/auth/logout/", { refresh: refreshToken })
      .then((r) => r.data),

  refreshToken: (refresh: string) =>
    apiClient
      .post<{ access: string; refresh?: string }>("/auth/token/refresh/", { refresh })
      .then((r) => r.data),

  getMe: () =>
    apiClient.get<User>("/auth/me/").then((r) => r.data),

  updateMe: (payload: Partial<Pick<User, "first_name" | "last_name" | "email" | "phone">> & { avatar?: File }) => {
    const isFileUpload = payload.avatar instanceof File;
    if (isFileUpload) {
      const form = new FormData();
      Object.entries(payload).forEach(([k, v]) => {
        if (v !== undefined) form.append(k, v as string | Blob);
      });
      return apiClient
        .patch<User>("/auth/me/", form, {
          headers: { "Content-Type": "multipart/form-data" },
        })
        .then((r) => r.data);
    }
    return apiClient.patch<User>("/auth/me/", payload).then((r) => r.data);
  },

  changePassword: (payload: ChangePasswordPayload) =>
    apiClient.post("/auth/change-password/", payload).then((r) => r.data),
};

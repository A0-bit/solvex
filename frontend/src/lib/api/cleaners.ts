import apiClient from "./client";
import type { CleanerUser } from "@/types/assignment";
import type { PaginatedResponse } from "@/types/report";

export interface CreateCleanerPayload {
  user_id: number;
  area?: number | null;
}

export const cleanersApi = {
  getCleaners: (params?: { area?: number }) =>
    apiClient
      .get<PaginatedResponse<CleanerUser>>("/cleaners/", { params })
      .then((r) => r.data),

  getCleaner: (id: number) =>
    apiClient.get<CleanerUser>(`/cleaners/${id}/`).then((r) => r.data),

  createCleaner: (payload: CreateCleanerPayload) =>
    apiClient.post<CleanerUser>("/cleaners/", payload).then((r) => r.data),

  updateCleaner: (
    id: number,
    patch: Partial<{ area: number | null; is_active: boolean }>
  ) =>
    apiClient.patch<CleanerUser>(`/cleaners/${id}/`, patch).then((r) => r.data),

  deleteCleaner: (id: number) =>
    apiClient.delete(`/cleaners/${id}/`).then((r) => r.data),
};

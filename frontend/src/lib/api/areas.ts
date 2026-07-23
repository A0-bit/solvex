import apiClient from "./client";
import type { Area, BoundaryPoint } from "@/types/area";
import type { PaginatedResponse } from "@/types/report";

export interface CreateAreaPayload {
  name: string;
  boundary: BoundaryPoint[];
  supervisor?: number | null;
}

export const areasApi = {
  getAreas: () =>
    apiClient
      .get<PaginatedResponse<Area>>("/areas/")
      .then((r) => r.data),

  getArea: (id: number) =>
    apiClient.get<Area>(`/areas/${id}/`).then((r) => r.data),

  createArea: (payload: CreateAreaPayload) =>
    apiClient.post<Area>("/areas/", payload).then((r) => r.data),

  updateArea: (id: number, patch: Partial<CreateAreaPayload>) =>
    apiClient.patch<Area>(`/areas/${id}/`, patch).then((r) => r.data),

  deleteArea: (id: number) =>
    apiClient.delete(`/areas/${id}/`).then((r) => r.data),
};

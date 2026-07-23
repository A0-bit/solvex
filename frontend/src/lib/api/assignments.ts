import apiClient from "./client";
import type { Assignment, CreateAssignmentPayload } from "@/types/assignment";

export const assignmentsApi = {
  createAssignment: (payload: CreateAssignmentPayload) =>
    apiClient.post<Assignment>("/assignments/", payload).then((r) => r.data),

  getAssignment: (id: number) =>
    apiClient.get<Assignment>(`/assignments/${id}/`).then((r) => r.data),

  updateAssignment: (id: number, patch: Partial<{ notes: string; completed_at: string }>) =>
    apiClient.patch<Assignment>(`/assignments/${id}/`, patch).then((r) => r.data),
};

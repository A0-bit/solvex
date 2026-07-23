import apiClient from "./client";
import type {
  Report,
  ReportListItem,
  PaginatedResponse,
  ReportStatus,
} from "@/types/report";

export const reportsApi = {
  /** GET /reports/ — own reports (user) */
  getMyReports: (params?: { status?: ReportStatus; page?: number }) =>
    apiClient
      .get<PaginatedResponse<ReportListItem>>("/reports/", { params })
      .then((r) => r.data),

  /** GET /reports/{id}/ */
  getReport: (id: number) =>
    apiClient.get<Report>(`/reports/${id}/`).then((r) => r.data),

  /** POST /reports/ — multipart form */
  createReport: (payload: FormData) =>
    apiClient
      .post<Report>("/reports/", payload, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data),

  /** PATCH /reports/{id}/status/ */
  updateReportStatus: (id: number, status: ReportStatus) =>
    apiClient
      .patch<Report>(`/reports/${id}/status/`, { status })
      .then((r) => r.data),

  /** PATCH /reports/{id}/after-photo/ */
  uploadAfterPhoto: (id: number, file: File) => {
    const form = new FormData();
    form.append("after_photo", file);
    return apiClient
      .patch<Report>(`/reports/${id}/after-photo/`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },

  /** GET /reports/area/ — supervisor scope */
  getAreaReports: (params?: { status?: ReportStatus; search?: string; page?: number }) =>
    apiClient
      .get<PaginatedResponse<ReportListItem>>("/reports/area/", { params })
      .then((r) => r.data),

  /** GET /reports/all/ — superadmin scope */
  getAllReports: (params?: { status?: ReportStatus; search?: string; page?: number }) =>
    apiClient
      .get<PaginatedResponse<ReportListItem>>("/reports/all/", { params })
      .then((r) => r.data),
};

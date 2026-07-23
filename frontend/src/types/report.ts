import type { User } from "./user";
import type { Area } from "./area";

export type ReportStatus =
  | "pending"
  | "assigned"
  | "in_progress"
  | "resolved"
  | "rejected";

export interface Assignment {
  id: number;
  cleaner_id: number | null;
  cleaner_name: string | null;
  notes: string;
  assigned_at: string;
  completed_at: string | null;
}

export interface Report {
  id: number;
  reporter: User;
  area: Area | null;
  title: string;
  description: string;
  latitude: string;
  longitude: string;
  before_photo: string;
  after_photo: string | null;
  status: ReportStatus;
  assignment: Assignment | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
}

export interface ReportListItem {
  id: number;
  title: string;
  status: ReportStatus;
  reporter_name: string;
  area_name: string | null;
  latitude: string;
  longitude: string;
  before_photo: string;
  created_at: string;
}

export interface CreateReportPayload {
  title: string;
  description: string;
  latitude: number;
  longitude: number;
  before_photo: File;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

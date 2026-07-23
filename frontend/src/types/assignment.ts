import type { ReportListItem } from "./report";
import type { User } from "./user";

export interface CleanerUser {
  id: number;
  user: User;
  area: number | null;
  area_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Assignment {
  id: number;
  report: number;
  report_detail: ReportListItem;
  cleaner: number | null;
  cleaner_detail: CleanerUser | null;
  assigned_by: number | null;
  assigned_by_detail: User | null;
  notes: string;
  assigned_at: string;
  completed_at: string | null;
}

export interface CreateAssignmentPayload {
  report: number;
  cleaner: number;
  notes?: string;
}

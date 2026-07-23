import type { ReportStatus } from "@/types/report";

export const STATUS_COLORS: Record<ReportStatus, string> = {
  pending: "bg-yellow-100 text-yellow-800 border-yellow-200",
  assigned: "bg-blue-100 text-blue-800 border-blue-200",
  in_progress: "bg-orange-100 text-orange-800 border-orange-200",
  resolved: "bg-green-100 text-green-800 border-green-200",
  rejected: "bg-red-100 text-red-800 border-red-200",
};

export const STATUS_LABELS: Record<ReportStatus, string> = {
  pending: "Pending",
  assigned: "Assigned",
  in_progress: "In Progress",
  resolved: "Resolved",
  rejected: "Rejected",
};

export function statusColor(status: ReportStatus): string {
  return STATUS_COLORS[status] ?? "bg-gray-100 text-gray-800";
}

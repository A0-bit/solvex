"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Image from "next/image";
import ReportStatusBadge from "@/components/reports/ReportStatusBadge";
import ReportMapView from "@/components/map/ReportMapView";
import AfterPhotoUpload from "@/components/reports/AfterPhotoUpload";
import AssignCleanerModal from "@/components/assignments/AssignCleanerModal";
import Button from "@/components/ui/Button";
import { reportsApi } from "@/lib/api/reports";
import { formatDateTime } from "@/lib/utils/formatDate";
import type { Report, ReportStatus } from "@/types/report";
import type { ReportListItem } from "@/types/report";

const SUPERVISOR_TRANSITIONS: Partial<Record<ReportStatus, ReportStatus[]>> = {
  assigned: ["in_progress", "rejected"],
  in_progress: ["resolved", "rejected"],
};

export default function SupervisorReportDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [assignOpen, setAssignOpen] = useState(false);
  const [statusLoading, setStatusLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    reportsApi.getReport(Number(id))
      .then(setReport)
      .finally(() => setLoading(false));
  }, [id]);

  async function changeStatus(newStatus: ReportStatus) {
    if (!report) return;
    setStatusLoading(true);
    setError(null);
    try {
      const updated = await reportsApi.updateReportStatus(report.id, newStatus);
      setReport(updated);
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string; status?: string[] } } })?.response?.data?.detail
        ?? (err as { response?: { data?: { status?: string[] } } })?.response?.data?.status?.[0]
        ?? "Status update failed.";
      setError(detail);
    } finally {
      setStatusLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-32 animate-pulse rounded-xl bg-gray-200" />
        ))}
      </div>
    );
  }

  if (!report) {
    return <div className="py-20 text-center text-sm text-gray-400">Report not found.</div>;
  }

  const availableTransitions = SUPERVISOR_TRANSITIONS[report.status] ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start gap-3">
        <button onClick={() => router.back()}
          className="mt-0.5 rounded-lg p-1.5 text-gray-400 hover:bg-gray-100">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-gray-900">{report.title}</h1>
          <div className="mt-1.5 flex flex-wrap items-center gap-2">
            <ReportStatusBadge status={report.status} />
            <span className="text-xs text-gray-400">{formatDateTime(report.created_at)}</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>
      )}

      {/* Action buttons */}
      <div className="flex flex-wrap gap-2">
        {/* Assign button — only when pending */}
        {report.status === "pending" && (
          <Button onClick={() => setAssignOpen(true)}>
            Assign Cleaner
          </Button>
        )}

        {/* Status transitions */}
        {availableTransitions.map((s) => (
          <Button
            key={s}
            variant={s === "rejected" ? "danger" : s === "resolved" ? "primary" : "secondary"}
            loading={statusLoading}
            onClick={() => changeStatus(s)}
          >
            Mark {s === "in_progress" ? "In Progress" : s.charAt(0).toUpperCase() + s.slice(1)}
          </Button>
        ))}
      </div>

      {/* Before/After photos */}
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Before</p>
          <div className="relative h-52 w-full overflow-hidden rounded-xl bg-gray-100">
            <Image src={report.before_photo} alt="Before" fill className="object-cover" />
          </div>
        </div>

        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">After</p>
          {report.after_photo ? (
            <div className="relative h-52 w-full overflow-hidden rounded-xl bg-gray-100">
              <Image src={report.after_photo} alt="After" fill className="object-cover" />
            </div>
          ) : (
            report.status === "in_progress" && (
              <AfterPhotoUpload
                reportId={report.id}
                onSuccess={(updated) => setReport(updated)}
              />
            )
          )}
        </div>
      </div>

      {/* Description */}
      {report.description && (
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500">Description</p>
          <p className="text-sm text-gray-700">{report.description}</p>
        </div>
      )}

      {/* Details */}
      <div className="rounded-xl border border-gray-200 bg-white p-4">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-500">Details</p>
        <dl className="space-y-2 text-sm">
          <div className="flex justify-between">
            <dt className="text-gray-500">Reported by</dt>
            <dd className="font-medium text-gray-900">
              {report.reporter.first_name
                ? `${report.reporter.first_name} ${report.reporter.last_name}`
                : report.reporter.username}
            </dd>
          </div>
          {report.area && (
            <div className="flex justify-between">
              <dt className="text-gray-500">Area</dt>
              <dd className="font-medium text-gray-900">{report.area.name}</dd>
            </div>
          )}
          {report.assignment && (
            <>
              <div className="flex justify-between">
                <dt className="text-gray-500">Assigned to</dt>
                <dd className="font-medium text-gray-900">
                  {report.assignment.cleaner_name ?? "—"}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Assigned at</dt>
                <dd className="font-medium text-gray-900">
                  {formatDateTime(report.assignment.assigned_at)}
                </dd>
              </div>
            </>
          )}
          {report.resolved_at && (
            <div className="flex justify-between">
              <dt className="text-gray-500">Resolved at</dt>
              <dd className="font-medium text-gray-900">{formatDateTime(report.resolved_at)}</dd>
            </div>
          )}
        </dl>
      </div>

      {/* Map */}
      <div>
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Location</p>
        <ReportMapView lat={Number(report.latitude)} lng={Number(report.longitude)} />
      </div>

      {/* Assign modal */}
      <AssignCleanerModal
        open={assignOpen}
        report={report as unknown as ReportListItem}
        onClose={() => setAssignOpen(false)}
        onAssigned={() => {
          reportsApi.getReport(report.id).then(setReport);
        }}
      />
    </div>
  );
}

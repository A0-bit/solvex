"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Image from "next/image";
import ReportStatusBadge from "@/components/reports/ReportStatusBadge";
import ReportMapView from "@/components/map/ReportMapView";
import { reportsApi } from "@/lib/api/reports";
import { formatDateTime } from "@/lib/utils/formatDate";
import type { Report } from "@/types/report";

export default function ReportDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    reportsApi.getReport(Number(id))
      .then(setReport)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 animate-pulse rounded-lg bg-gray-200" />
        <div className="h-56 animate-pulse rounded-xl bg-gray-200" />
        <div className="h-32 animate-pulse rounded-xl bg-gray-200" />
      </div>
    );
  }

  if (!report) {
    return (
      <div className="py-20 text-center text-sm text-gray-400">Report not found.</div>
    );
  }

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-start gap-3">
        <button onClick={() => router.back()} className="mt-0.5 rounded-lg p-1.5 text-gray-400 hover:bg-gray-100">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div>
          <h1 className="text-lg font-bold text-gray-900">{report.title}</h1>
          <div className="mt-1 flex items-center gap-2">
            <ReportStatusBadge status={report.status} />
            <span className="text-xs text-gray-400">{formatDateTime(report.created_at)}</span>
          </div>
        </div>
      </div>

      {/* Before photo */}
      <div>
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Before</p>
        <div className="relative h-56 w-full overflow-hidden rounded-xl bg-gray-100">
          <Image src={report.before_photo} alt="Before" fill className="object-cover" />
        </div>
      </div>

      {/* After photo */}
      {report.after_photo && (
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">After</p>
          <div className="relative h-56 w-full overflow-hidden rounded-xl bg-gray-100">
            <Image src={report.after_photo} alt="After" fill className="object-cover" />
          </div>
        </div>
      )}

      {/* Description */}
      {report.description && (
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Description</p>
          <p className="mt-1 text-sm text-gray-700">{report.description}</p>
        </div>
      )}

      {/* Details */}
      <div className="rounded-xl border border-gray-200 bg-white p-4 text-sm">
        <dl className="space-y-2">
          {report.area && (
            <div className="flex justify-between">
              <dt className="text-gray-500">Area</dt>
              <dd className="font-medium text-gray-900">{report.area.name}</dd>
            </div>
          )}
          {report.assignment?.cleaner_name && (
            <div className="flex justify-between">
              <dt className="text-gray-500">Assigned to</dt>
              <dd className="font-medium text-gray-900">{report.assignment.cleaner_name}</dd>
            </div>
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
    </div>
  );
}

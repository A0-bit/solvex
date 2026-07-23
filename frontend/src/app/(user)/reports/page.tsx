"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import ReportCard from "@/components/reports/ReportCard";
import { reportsApi } from "@/lib/api/reports";
import type { ReportListItem, ReportStatus } from "@/types/report";
import { STATUS_LABELS } from "@/lib/utils/statusColor";

const STATUS_FILTERS: Array<{ value: ReportStatus | ""; label: string }> = [
  { value: "", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "assigned", label: "Assigned" },
  { value: "in_progress", label: "In Progress" },
  { value: "resolved", label: "Resolved" },
  { value: "rejected", label: "Rejected" },
];

export default function UserReportsPage() {
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [status, setStatus] = useState<ReportStatus | "">("");
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);

  const load = useCallback(async (s: ReportStatus | "", p: number) => {
    setLoading(true);
    try {
      const data = await reportsApi.getMyReports({ status: s || undefined, page: p });
      setReports(p === 1 ? data.results : (prev) => [...prev, ...data.results]);
      setHasNext(!!data.next);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setPage(1);
    load(status, 1);
  }, [status, load]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-bold text-gray-900">My Reports</h1>
        <Link
          href="/reports/new"
          className="rounded-lg bg-green-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-green-700"
        >
          + New
        </Link>
      </div>

      {/* Status filter chips */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        {STATUS_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => setStatus(f.value)}
            className={`flex-shrink-0 rounded-full px-3 py-1 text-xs font-medium transition ${
              status === f.value
                ? "bg-green-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* List */}
      {loading && reports.length === 0 ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 animate-pulse rounded-xl bg-gray-200" />
          ))}
        </div>
      ) : reports.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-300 py-12 text-center text-sm text-gray-400">
          No reports found.
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map((r) => (
            <ReportCard key={r.id} report={r} href={`/reports/${r.id}`} />
          ))}
        </div>
      )}

      {hasNext && (
        <button
          onClick={() => {
            const next = page + 1;
            setPage(next);
            load(status, next);
          }}
          disabled={loading}
          className="w-full rounded-lg border border-gray-300 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50"
        >
          {loading ? "Loading…" : "Load more"}
        </button>
      )}
    </div>
  );
}

"use client";

import { useEffect, useState, useCallback } from "react";
import ReportCard from "@/components/reports/ReportCard";
import { reportsApi } from "@/lib/api/reports";
import type { ReportListItem, ReportStatus } from "@/types/report";

const STATUS_FILTERS: Array<{ value: ReportStatus | ""; label: string }> = [
  { value: "", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "assigned", label: "Assigned" },
  { value: "in_progress", label: "In Progress" },
  { value: "resolved", label: "Resolved" },
  { value: "rejected", label: "Rejected" },
];

export default function SupervisorReportsPage() {
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [status, setStatus] = useState<ReportStatus | "">("");
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);

  // Debounce search
  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 400);
    return () => clearTimeout(t);
  }, [search]);

  const load = useCallback(async (s: ReportStatus | "", q: string, p: number) => {
    setLoading(true);
    try {
      const data = await reportsApi.getAreaReports({
        status: s || undefined,
        search: q || undefined,
        page: p,
      });
      setReports(p === 1 ? data.results : (prev) => [...prev, ...data.results]);
      setHasNext(!!data.next);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setPage(1);
    load(status, debouncedSearch, 1);
  }, [status, debouncedSearch, load]);

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-bold text-gray-900">Area Reports</h1>

      {/* Search */}
      <div className="relative">
        <svg className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400"
          fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          type="text"
          placeholder="Search reports…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-lg border border-gray-300 py-2 pl-9 pr-3 text-sm outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100"
        />
      </div>

      {/* Status filters */}
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

      {/* Report list */}
      {loading && reports.length === 0 ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 animate-pulse rounded-xl bg-gray-200" />
          ))}
        </div>
      ) : reports.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-300 py-16 text-center text-sm text-gray-400">
          No reports match your filters.
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map((r) => (
            <ReportCard key={r.id} report={r} href={`/supervisor/reports/${r.id}`} />
          ))}
        </div>
      )}

      {hasNext && (
        <button
          onClick={() => { const next = page + 1; setPage(next); load(status, debouncedSearch, next); }}
          disabled={loading}
          className="w-full rounded-lg border border-gray-300 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50"
        >
          {loading ? "Loading…" : "Load more"}
        </button>
      )}
    </div>
  );
}

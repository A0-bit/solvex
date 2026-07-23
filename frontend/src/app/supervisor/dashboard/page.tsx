"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuthStore } from "@/store/authStore";
import ReportCard from "@/components/reports/ReportCard";
import { reportsApi } from "@/lib/api/reports";
import type { ReportListItem } from "@/types/report";

interface Stats {
  area: string;
  total_reports: number;
  reports_by_status: Record<string, number>;
  active_cleaners: number;
}

export default function SupervisorDashboard() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<Stats | null>(null);
  const [recent, setRecent] = useState<ReportListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token =
      typeof window !== "undefined"
        ? (JSON.parse(localStorage.getItem("auth-storage") || "{}")?.state?.accessToken ?? "")
        : "";

    Promise.all([
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/stats/supervisor/`, {
        headers: { Authorization: `Bearer ${token}` },
      }).then((r) => r.json()),
      reportsApi.getAreaReports({ page: 1 }),
    ])
      .then(([statsData, reports]) => {
        setStats(statsData);
        setRecent(reports.results.slice(0, 5));
      })
      .finally(() => setLoading(false));
  }, []);

  const statusCards = [
    { label: "Pending", key: "pending", color: "bg-yellow-50 border-yellow-200 text-yellow-700" },
    { label: "Assigned", key: "assigned", color: "bg-blue-50 border-blue-200 text-blue-700" },
    { label: "In Progress", key: "in_progress", color: "bg-orange-50 border-orange-200 text-orange-700" },
    { label: "Resolved", key: "resolved", color: "bg-green-50 border-green-200 text-green-700" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.first_name || user?.username}
        </h1>
        {stats?.area && (
          <p className="mt-1 text-sm text-gray-500">
            Managing area: <span className="font-medium text-gray-700">{stats.area}</span>
          </p>
        )}
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {statusCards.map((s) => (
          <div key={s.key} className={`rounded-xl border p-4 ${s.color}`}>
            <p className="text-3xl font-bold">
              {loading ? "—" : stats?.reports_by_status?.[s.key] ?? 0}
            </p>
            <p className="mt-1 text-sm font-medium">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Summary bar */}
      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <p className="text-3xl font-bold text-gray-900">
            {loading ? "—" : stats?.total_reports ?? 0}
          </p>
          <p className="mt-1 text-sm text-gray-500">Total Reports</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <p className="text-3xl font-bold text-gray-900">
            {loading ? "—" : stats?.active_cleaners ?? 0}
          </p>
          <p className="mt-1 text-sm text-gray-500">Active Cleaners</p>
        </div>
      </div>

      {/* Recent unassigned */}
      <div>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="font-semibold text-gray-800">Recent Reports</h2>
          <Link href="/supervisor/reports" className="text-sm font-medium text-green-600 hover:underline">
            View all →
          </Link>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 animate-pulse rounded-xl bg-gray-200" />
            ))}
          </div>
        ) : recent.length === 0 ? (
          <div className="rounded-xl border border-dashed border-gray-300 py-12 text-center text-sm text-gray-400">
            No reports in your area yet.
          </div>
        ) : (
          <div className="space-y-3">
            {recent.map((r) => (
              <ReportCard key={r.id} report={r} href={`/supervisor/reports/${r.id}`} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

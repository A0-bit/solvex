"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuthStore } from "@/store/authStore";
import ReportCard from "@/components/reports/ReportCard";
import { reportsApi } from "@/lib/api/reports";
import type { ReportListItem } from "@/types/report";

interface Stats {
  total_reports: number;
  reports_by_status: Record<string, number>;
}

export default function UserDashboard() {
  const { user } = useAuthStore();
  const [recent, setRecent] = useState<ReportListItem[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      reportsApi.getMyReports({ page: 1 }),
      fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/stats/user/`,
        {
          headers: {
            Authorization: `Bearer ${
              typeof window !== "undefined"
                ? JSON.parse(localStorage.getItem("auth-storage") || "{}")?.state?.accessToken
                : ""
            }`,
          },
        }
      ).then((r) => r.json()),
    ])
      .then(([reports, statsData]) => {
        setRecent(reports.results.slice(0, 3));
        setStats(statsData);
      })
      .finally(() => setLoading(false));
  }, []);

  const statusCards = [
    { label: "Pending", key: "pending", color: "bg-yellow-50 border-yellow-200 text-yellow-700" },
    { label: "In Progress", key: "in_progress", color: "bg-orange-50 border-orange-200 text-orange-700" },
    { label: "Resolved", key: "resolved", color: "bg-green-50 border-green-200 text-green-700" },
  ];

  return (
    <div className="space-y-6">
      {/* Greeting */}
      <div>
        <h1 className="text-xl font-bold text-gray-900">
          Hello, {user?.first_name || user?.username} 👋
        </h1>
        <p className="text-sm text-gray-500">Here's what's happening with your reports.</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3">
        {statusCards.map((s) => (
          <div key={s.key} className={`rounded-xl border p-3 text-center ${s.color}`}>
            <p className="text-2xl font-bold">
              {loading ? "—" : stats?.reports_by_status?.[s.key] ?? 0}
            </p>
            <p className="text-xs font-medium">{s.label}</p>
          </div>
        ))}
      </div>

      {/* New report CTA */}
      <Link
        href="/reports/new"
        className="flex items-center justify-center gap-2 rounded-xl bg-green-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-green-700"
      >
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        Report Garbage
      </Link>

      {/* Recent reports */}
      <div>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-700">Recent Reports</h2>
          <Link href="/reports" className="text-xs font-medium text-green-600 hover:underline">
            View all
          </Link>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 animate-pulse rounded-xl bg-gray-200" />
            ))}
          </div>
        ) : recent.length === 0 ? (
          <div className="rounded-xl border border-dashed border-gray-300 py-10 text-center text-sm text-gray-400">
            No reports yet. Tap "Report Garbage" to get started.
          </div>
        ) : (
          <div className="space-y-3">
            {recent.map((r) => (
              <ReportCard key={r.id} report={r} href={`/reports/${r.id}`} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

import Link from "next/link";
import Image from "next/image";
import ReportStatusBadge from "./ReportStatusBadge";
import { timeAgo } from "@/lib/utils/formatDate";
import type { ReportListItem } from "@/types/report";

interface Props {
  report: ReportListItem;
  href: string;
}

export default function ReportCard({ report, href }: Props) {
  return (
    <Link
      href={href}
      className="flex gap-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition hover:border-green-300 hover:shadow-md"
    >
      {/* Thumbnail */}
      <div className="relative h-20 w-20 flex-shrink-0 overflow-hidden rounded-lg bg-gray-100">
        {report.before_photo ? (
          <Image
            src={report.before_photo}
            alt={report.title}
            fill
            className="object-cover"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-gray-300">
            <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="min-w-0 flex-1">
        <div className="mb-1 flex items-start justify-between gap-2">
          <h3 className="truncate text-sm font-semibold text-gray-900">{report.title}</h3>
          <ReportStatusBadge status={report.status} />
        </div>
        {report.area_name && (
          <p className="mb-1 text-xs text-gray-500">
            <svg className="mr-1 inline h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {report.area_name}
          </p>
        )}
        <p className="text-xs text-gray-400">{timeAgo(report.created_at)}</p>
      </div>
    </Link>
  );
}

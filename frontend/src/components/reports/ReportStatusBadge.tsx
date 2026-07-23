import Badge from "@/components/ui/Badge";
import { STATUS_LABELS } from "@/lib/utils/statusColor";
import type { ReportStatus } from "@/types/report";

const STATUS_BADGE_VARIANTS: Record<
  ReportStatus,
  "yellow" | "blue" | "orange" | "green" | "red"
> = {
  pending: "yellow",
  assigned: "blue",
  in_progress: "orange",
  resolved: "green",
  rejected: "red",
};

interface ReportStatusBadgeProps {
  status: ReportStatus;
  className?: string;
}

export default function ReportStatusBadge({
  status,
  className,
}: ReportStatusBadgeProps) {
  return (
    <Badge variant={STATUS_BADGE_VARIANTS[status]} className={className}>
      {STATUS_LABELS[status] ?? status}
    </Badge>
  );
}

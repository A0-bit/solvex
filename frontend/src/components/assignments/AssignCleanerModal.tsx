"use client";

import { useEffect, useState } from "react";
import Modal from "@/components/ui/Modal";
import Button from "@/components/ui/Button";
import { cleanersApi } from "@/lib/api/cleaners";
import { assignmentsApi } from "@/lib/api/assignments";
import type { CleanerUser } from "@/types/assignment";
import type { ReportListItem } from "@/types/report";

interface Props {
  report: ReportListItem | null;
  open: boolean;
  onClose: () => void;
  onAssigned: () => void;
}

export default function AssignCleanerModal({ report, open, onClose, onAssigned }: Props) {
  const [cleaners, setCleaners] = useState<CleanerUser[]>([]);
  const [selectedCleaner, setSelectedCleaner] = useState<number | "">("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    cleanersApi.getCleaners().then((data) => setCleaners(data.results ?? []));
  }, [open]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedCleaner || !report) return;
    setLoading(true);
    setError(null);
    try {
      await assignmentsApi.createAssignment({
        report: report.id,
        cleaner: selectedCleaner as number,
        notes,
      });
      onAssigned();
      onClose();
    } catch {
      setError("Failed to assign cleaner. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Assign Cleaner">
      {report && (
        <p className="mb-4 text-sm text-gray-600">
          Assigning cleaner for: <span className="font-medium text-gray-900">{report.title}</span>
        </p>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Select Cleaner <span className="text-red-500">*</span>
          </label>
          <select
            value={selectedCleaner}
            onChange={(e) => setSelectedCleaner(Number(e.target.value))}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100"
          >
            <option value="">-- Choose a cleaner --</option>
            {cleaners.map((c) => (
              <option key={c.id} value={c.id}>
                {c.user.first_name
                  ? `${c.user.first_name} ${c.user.last_name}`
                  : c.user.username}
                {!c.is_active && " (inactive)"}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Notes (optional)</label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            placeholder="Any special instructions..."
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100"
          />
        </div>

        {error && <p className="text-xs text-red-600">{error}</p>}

        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={loading} disabled={!selectedCleaner}>
            Assign
          </Button>
        </div>
      </form>
    </Modal>
  );
}

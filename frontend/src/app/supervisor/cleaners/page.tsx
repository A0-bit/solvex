"use client";

import { useEffect, useState } from "react";
import { cleanersApi } from "@/lib/api/cleaners";
import { authApi } from "@/lib/api/auth";
import Button from "@/components/ui/Button";
import Modal from "@/components/ui/Modal";
import Input from "@/components/ui/Input";
import type { CleanerUser } from "@/types/assignment";
import type { User } from "@/types/user";

export default function SupervisorCleanersPage() {
  const [cleaners, setCleaners] = useState<CleanerUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [addOpen, setAddOpen] = useState(false);

  function loadCleaners() {
    cleanersApi
      .getCleaners()
      .then((data) => setCleaners(data.results ?? []))
      .finally(() => setLoading(false));
  }

  useEffect(() => { loadCleaners(); }, []);

  async function handleDeactivate(id: number) {
    if (!confirm("Deactivate this cleaner?")) return;
    await cleanersApi.updateCleaner(id, { is_active: false });
    loadCleaners();
  }

  async function handleActivate(id: number) {
    await cleanersApi.updateCleaner(id, { is_active: true });
    loadCleaners();
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Cleaners</h1>
        <Button onClick={() => setAddOpen(true)} size="sm">+ Add Cleaner</Button>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 animate-pulse rounded-xl bg-gray-200" />
          ))}
        </div>
      ) : cleaners.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-300 py-16 text-center text-sm text-gray-400">
          No cleaners assigned to your area yet.
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
          <table className="w-full text-sm">
            <thead className="border-b border-gray-200 bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Name</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Username</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Status</th>
                <th className="px-4 py-3 text-right font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {cleaners.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {c.user.first_name
                      ? `${c.user.first_name} ${c.user.last_name}`
                      : c.user.username}
                  </td>
                  <td className="px-4 py-3 text-gray-500">@{c.user.username}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        c.is_active
                          ? "bg-green-100 text-green-700"
                          : "bg-gray-100 text-gray-500"
                      }`}
                    >
                      {c.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    {c.is_active ? (
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDeactivate(c.id)}
                      >
                        Deactivate
                      </Button>
                    ) : (
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleActivate(c.id)}
                      >
                        Activate
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <AddCleanerModal
        open={addOpen}
        onClose={() => setAddOpen(false)}
        onAdded={() => { loadCleaners(); setAddOpen(false); }}
      />
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Add Cleaner Modal — search users then register as cleaner           */
/* ------------------------------------------------------------------ */

function AddCleanerModal({
  open,
  onClose,
  onAdded,
}: {
  open: boolean;
  onClose: () => void;
  onAdded: () => void;
}) {
  const [step, setStep] = useState<"search" | "create">("search");
  const [users, setUsers] = useState<User[]>([]);
  const [searchQ, setSearchQ] = useState("");
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // New user creation fields
  const [newUser, setNewUser] = useState({
    username: "", email: "", password: "", password2: "", first_name: "", last_name: "",
  });

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      // Fetch all users and filter client-side (SuperAdmin only endpoint — supervisor uses their own cleaner area)
      // For supervisor flow we create the user then assign; simplified here
      setError("Use the 'Create New User' option to add a cleaner account.");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (newUser.password !== newUser.password2) {
      setError("Passwords do not match."); return;
    }
    setLoading(true);
    setError(null);
    try {
      const created = await authApi.register({ ...newUser, role: "user" });
      await cleanersApi.createCleaner({ user_id: created.id });
      onAdded();
    } catch (err: unknown) {
      const data = (err as { response?: { data?: Record<string, string[]> } })?.response?.data;
      const first = data ? Object.values(data).flat()[0] : "Failed to create cleaner.";
      setError(first ?? "Failed to create cleaner.");
    } finally {
      setLoading(false);
    }
  }

  function resetAndClose() {
    setStep("search");
    setNewUser({ username: "", email: "", password: "", password2: "", first_name: "", last_name: "" });
    setError(null);
    onClose();
  }

  return (
    <Modal open={open} onClose={resetAndClose} title="Add Cleaner">
      {/* Tab switch */}
      <div className="mb-5 flex rounded-lg border border-gray-200 p-1">
        {(["search", "create"] as const).map((t) => (
          <button
            key={t}
            onClick={() => { setStep(t); setError(null); }}
            className={`flex-1 rounded-md py-1.5 text-sm font-medium transition ${
              step === t ? "bg-green-600 text-white shadow-sm" : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {t === "search" ? "Existing User" : "Create New User"}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>
      )}

      {step === "search" ? (
        <div className="space-y-3 text-sm text-gray-500">
          <p>To assign an existing user as a cleaner, use the Django Admin panel or ask a SuperAdmin.</p>
          <Button variant="secondary" onClick={() => setStep("create")} className="w-full">
            Create New Cleaner Account Instead
          </Button>
        </div>
      ) : (
        <form onSubmit={handleCreate} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="First name"
              required
              value={newUser.first_name}
              onChange={(e) => setNewUser((p) => ({ ...p, first_name: e.target.value }))}
            />
            <Input
              label="Last name"
              value={newUser.last_name}
              onChange={(e) => setNewUser((p) => ({ ...p, last_name: e.target.value }))}
            />
          </div>
          <Input
            label="Username"
            required
            value={newUser.username}
            onChange={(e) => setNewUser((p) => ({ ...p, username: e.target.value }))}
          />
          <Input
            label="Email"
            type="email"
            required
            value={newUser.email}
            onChange={(e) => setNewUser((p) => ({ ...p, email: e.target.value }))}
          />
          <Input
            label="Password"
            type="password"
            required
            value={newUser.password}
            onChange={(e) => setNewUser((p) => ({ ...p, password: e.target.value }))}
          />
          <Input
            label="Confirm Password"
            type="password"
            required
            value={newUser.password2}
            onChange={(e) => setNewUser((p) => ({ ...p, password2: e.target.value }))}
          />
          <div className="flex justify-end gap-2 pt-1">
            <Button type="button" variant="secondary" onClick={resetAndClose}>Cancel</Button>
            <Button type="submit" loading={loading}>Create & Add</Button>
          </div>
        </form>
      )}
    </Modal>
  );
}

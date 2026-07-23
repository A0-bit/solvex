"use client";

import { useState } from "react";
import Image from "next/image";
import { useAuthStore } from "@/store/authStore";
import { authApi } from "@/lib/api/auth";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";

export default function ProfilePage() {
  const { user, setUser } = useAuthStore();
  const [form, setForm] = useState({
    first_name: user?.first_name ?? "",
    last_name: user?.last_name ?? "",
    email: user?.email ?? "",
    phone: user?.phone ?? "",
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function update(field: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((p) => ({ ...p, [field]: e.target.value }));
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setSuccess(false);
    setError(null);
    try {
      const updated = await authApi.updateMe(form);
      setUser(updated);
      setSuccess(true);
    } catch {
      setError("Failed to update profile.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-lg font-bold text-gray-900">Profile</h1>

      {/* Avatar */}
      <div className="flex items-center gap-4">
        <div className="relative h-16 w-16 overflow-hidden rounded-full bg-green-100">
          {user?.avatar ? (
            <Image src={user.avatar} alt={user.username} fill className="object-cover" />
          ) : (
            <div className="flex h-full w-full items-center justify-center text-xl font-bold text-green-700">
              {(user?.first_name?.[0] ?? user?.username?.[0] ?? "U").toUpperCase()}
            </div>
          )}
        </div>
        <div>
          <p className="font-semibold text-gray-900">{user?.username}</p>
          <span className="inline-block rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 capitalize">
            {user?.role}
          </span>
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-4">
        {success && (
          <div className="rounded-lg bg-green-50 p-3 text-sm text-green-700">
            Profile updated successfully.
          </div>
        )}
        {error && (
          <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>
        )}

        <div className="grid grid-cols-2 gap-3">
          <Input label="First name" value={form.first_name} onChange={update("first_name")} />
          <Input label="Last name" value={form.last_name} onChange={update("last_name")} />
        </div>
        <Input label="Email" type="email" value={form.email} onChange={update("email")} />
        <Input label="Phone" type="tel" value={form.phone} onChange={update("phone")} />

        <Button type="submit" loading={loading} className="w-full">
          Save Changes
        </Button>
      </form>
    </div>
  );
}

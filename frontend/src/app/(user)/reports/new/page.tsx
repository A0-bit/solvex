"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { reportsApi } from "@/lib/api/reports";

const LocationPicker = dynamic(
  () => import("@/components/map/LocationPicker"),
  { ssr: false, loading: () => <div className="h-[300px] animate-pulse rounded-lg bg-gray-200" /> }
);

export default function NewReportPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [lat, setLat] = useState<number | null>(null);
  const [lng, setLng] = useState<number | null>(null);
  const [gpsPosition, setGpsPosition] = useState<[number, number] | undefined>();
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Auto-detect GPS on mount
  useEffect(() => {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const p: [number, number] = [pos.coords.latitude, pos.coords.longitude];
        setGpsPosition(p);
        setLat(p[0]);
        setLng(p[1]);
      },
      () => {} // silently fail
    );
  }, []);

  function handlePhotoChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 10 * 1024 * 1024) {
      setErrors((prev) => ({ ...prev, photo: "Photo must be under 10 MB." }));
      return;
    }
    setPhoto(f);
    setPhotoPreview(URL.createObjectURL(f));
    setErrors((prev) => ({ ...prev, photo: "" }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const errs: Record<string, string> = {};
    if (!title.trim()) errs.title = "Title is required.";
    if (!photo) errs.photo = "Before photo is required.";
    if (lat === null || lng === null) errs.location = "Please pick a location on the map.";
    if (Object.keys(errs).length) { setErrors(errs); return; }

    const form = new FormData();
    form.append("title", title);
    form.append("description", description);
    form.append("latitude", String(lat));
    form.append("longitude", String(lng));
    form.append("before_photo", photo!);

    setLoading(true);
    try {
      const report = await reportsApi.createReport(form);
      router.replace(`/reports/${report.id}`);
    } catch (err: unknown) {
      const data = (err as { response?: { data?: Record<string, string[]> } })?.response?.data;
      if (data) {
        const mapped: Record<string, string> = {};
        Object.entries(data).forEach(([k, v]) => { mapped[k] = Array.isArray(v) ? v[0] : String(v); });
        setErrors(mapped);
      } else {
        setErrors({ general: "Submission failed. Please try again." });
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <button onClick={() => router.back()} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h1 className="text-lg font-bold text-gray-900">New Report</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {errors.general && (
          <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{errors.general}</div>
        )}

        <Input
          label="Title"
          required
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. Overflowing bin near park"
          error={errors.title}
        />

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            placeholder="More details about the issue..."
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100"
          />
        </div>

        {/* Before photo */}
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Before Photo <span className="text-red-500">*</span>
          </label>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={handlePhotoChange}
          />
          {photoPreview ? (
            <div className="relative">
              <img src={photoPreview} alt="Preview" className="h-48 w-full rounded-lg object-cover" />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="absolute bottom-2 right-2 rounded-lg bg-black/50 px-2 py-1 text-xs text-white hover:bg-black/70"
              >Change</button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="flex w-full flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-gray-300 py-8 text-sm text-gray-500 transition hover:border-green-400 hover:text-green-600"
            >
              <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Tap to take / upload photo
            </button>
          )}
          {errors.photo && <p className="mt-1 text-xs text-red-600">{errors.photo}</p>}
        </div>

        {/* Map */}
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Location <span className="text-red-500">*</span>
          </label>
          <LocationPicker
            onChange={(la, ln) => { setLat(la); setLng(ln); }}
            initialPosition={gpsPosition}
          />
          {errors.location && <p className="mt-1 text-xs text-red-600">{errors.location}</p>}
        </div>

        <Button type="submit" loading={loading} className="w-full" size="lg">
          Submit Report
        </Button>
      </form>
    </div>
  );
}

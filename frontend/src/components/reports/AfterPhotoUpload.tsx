"use client";

import { useRef, useState } from "react";
import Image from "next/image";
import Button from "@/components/ui/Button";
import { reportsApi } from "@/lib/api/reports";
import type { Report } from "@/types/report";

interface Props {
  reportId: number;
  onSuccess: (updated: Report) => void;
}

export default function AfterPhotoUpload({ reportId, onSuccess }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 10 * 1024 * 1024) {
      setError("File must be under 10 MB.");
      return;
    }
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setError(null);
  }

  async function handleUpload() {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const updated = await reportsApi.uploadAfterPhoto(reportId, file);
      onSuccess(updated);
    } catch {
      setError("Upload failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-3">
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={handleFileChange}
      />

      {preview ? (
        <div className="relative h-48 w-full overflow-hidden rounded-lg bg-gray-100">
          <Image src={preview} alt="After photo preview" fill className="object-cover" />
        </div>
      ) : (
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="flex w-full flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-gray-300 py-8 text-sm text-gray-500 transition hover:border-green-400 hover:text-green-600"
        >
          <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          Click to upload after photo
        </button>
      )}

      {error && <p className="text-xs text-red-600">{error}</p>}

      {preview && (
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={() => inputRef.current?.click()}>
            Change
          </Button>
          <Button size="sm" loading={loading} onClick={handleUpload}>
            Upload After Photo
          </Button>
        </div>
      )}
    </div>
  );
}
